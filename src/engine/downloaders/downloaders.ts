import {buildFile} from "./dl-file-processing";
import DBDownload, {DownloadSubscriber} from "../database/entities/db-download";
import promisePool, {mutex} from "../util/promise-pool";
import DBSetting from "../database/entities/db-setting";
import {makeName} from "../util/name-generator";
import {DBPost} from "../database/db";
import DBUrl from "../database/entities/db-url";
import Downloader, {GracefulStopError} from "./wrappers/download-wrapper";
import {v4} from "uuid";
import {DownloaderState, DownloadProgress} from "../util/state";
import YtdlDownloader from "./wrappers/ytdl-downloader";
import {getAbsoluteDL} from "../util/paths";
import {DirectDownloader} from "./wrappers/direct-downloader";
import {ImgurDownloader} from "./wrappers/imgur-downloader";
import {isTest} from "../util/config";
import DBFile from "../database/entities/db-file";
import {GfycatDownloader} from "./wrappers/gfycat-downloader";


let downloadList: Downloader[] = [];

export async function getDownloaders(): Promise<Downloader[]> {
    if (!downloadList.length) {
        downloadList = [new YtdlDownloader(), new DirectDownloader(), new ImgurDownloader(), new GfycatDownloader()];
    }

    for (const l of downloadList) {
        await l.initOnce();
        l.order = await l.getOrder();  // Buffer this before sorting.
    }

    return downloadList.sort((a, b) => a.order - b.order);
}


/**
 * Find the next DBDownload that needs a URL processed, which is not already inside the given array.
 *
 * This is a mutex, and can only be invoked with one concurrent lookup.
 */
export const getNextPendingDownload = mutex(async (ignoreURLs: Set<string>) => {
    let query = DBDownload.createQueryBuilder('dl')
        .leftJoinAndSelect('dl.url', 'url')
        .where("url.processed = :processed", {processed: false});

    if (ignoreURLs.size) {
        query = query.andWhere("url.address NOT IN (:...addrs)", {addrs: Array.from(ignoreURLs)});
    }

    return query.getOne();
});


/**
 * Run the downloading process for all unhandled DBUrls, and any that are saved live.
 */
export async function downloadAll(state: DownloaderState) {
    const pending = new Set<string>();
    const getNext = async() => (await getNextPendingDownload(pending)) || await DownloadSubscriber.awaitNew();

    return promisePool(async (stop, threadNumber) => {
        const nxt = await getNext();
        if (!nxt || state.shouldStop) return stop();
        if (pending.has(nxt.url.address)) return;  // Prevent duplicate URLs from downloading concurrently.
        pending.add(nxt.url.address);

        try {
            state.activeDownloads[threadNumber] = new DownloadProgress(threadNumber);
            await handleDownload(nxt, state.activeDownloads[threadNumber]!); // fetch the proxied object back.
            state.activeDownloads[threadNumber] = null;
        } catch (err) {
            console.error(err);
        }

        pending.delete(nxt.url.address);
    }, await DBSetting.get('concurrentThreads'), err => {
        console.error(err);
    });
}


export interface DownloaderData {
    /** The relative path of this file. */
    relativeFile: string,
    /** The target output file's absolute path */
    file: string;
    /** The target URL, unpacked from dl.url.address for simplicity */
    url: string;
    /** The Post providing this URL */
    post: DBPost;
    /** The DBDownload object providing this URL. */
    dl: DBDownload;
}

export interface DownloaderFunctions {
    /** Register a new list of URLs, and sets the current URL as an album parent. Noop for nested albums. */
    addAlbumUrls: (url: string[]) => Promise<null>;
    /** Mark the current URL as failed, and add a reason. The URL will be skipped by default after this. */
    markInvalid: (reason: string) => Promise<void>;
    /** gracefully exit in a way that will be swallowed by the parent error handling. */
    userExit: (reason?: string) => void;
}

const usedRelativeFileNames: string[] = [];

/**
 * Generate the data structure and callbacks that are to be passed into the Downloader instances.
 */
export async function buildDownloadData(dl: DBDownload, prog: DownloadProgress) {
    const relativeFile = await makeName(dl, await DBSetting.get('outputTemplate'), usedRelativeFileNames);

    usedRelativeFileNames[prog.thread] = relativeFile;  // Prevent this path from generating again until we overwrite it.
    prog.fileName = relativeFile;

    const data: DownloaderData = {
        relativeFile,
        file: getAbsoluteDL(relativeFile),
        url: dl.url.address,
        post: await dl.getDBParent(),
        dl
    };

    let albumIDX = 1;
    const callbacks: DownloaderFunctions = {
        addAlbumUrls: async (urls: string[]) => {
            if (dl.albumID && !dl.isAlbumParent) return null;  // Disallow nested albums.
            if (!dl.albumID) {
                const file = DBFile.build({
                    dHash: '',
                    hash1: '',
                    hash2: '',
                    hash3: '',
                    hash4: '',
                    isDir: true,
                    mimeType: '',
                    path: relativeFile + '/',  // Make this a directory for children downloads.
                    shaHash: "",
                    size: 0,
                }).save();
                dl.albumID = v4();
                dl.isAlbumParent = true;
                dl.url.file = file;
                await dl.url.save();
                await dl.save();  // Preserve ID for subsequent saved children.
            }
            const padLen = Math.ceil(Math.log(urls.length)/Math.log(10));
            for (const url of urls) {
                await DBDownload.getDownloader(data.post, url, dl.albumID).then(d => {
                    d.albumPaddedIndex = `${(albumIDX++)}`.padStart(padLen, '0');
                    return d.save()
                });
            }
            return null;
        },
        markInvalid: async (reason: string) => {
            await dl.url.setFailed(reason);
        },
        userExit: (reason?: string) => {throw new GracefulStopError(reason||'User exit')}
    };

    return {data, callbacks};
}

/**
 * Iterate through all available downloaders, attempting to handle the given DBDownload.
 */
export async function handleDownload(dl: DBDownload, progress: DownloadProgress) {
    const {data, callbacks} = await buildDownloadData(dl, progress);

    for (const d of await getDownloaders()) {
        if (progress.shouldStop || dl.url.processed) break;
        progress.status = `Looking for downloaders to handle this URL...`;
        if (await d.canHandle(data).catch(console.error)) {
            progress.handler = d.name;
            progress.status = `Downloading the URL...`;
            progress.knowsPercent = false;
            progress.percent = 0;

            try {
                let ext = await d.download(data, callbacks, progress);
                if (dl.url.failed || dl.url.processed) continue;
                if (dl.isAlbumParent) {
                    dl.url.failed = false;
                    dl.url.failureReason = null;
                    dl.url.processed = true;
                    dl.url.completedUTC = Date.now();
                    dl.url.handler = d.name;
                    await dl.save();
                    return;
                }
                if (!ext) {
                    if (isTest()) console.warn('handler:', d.name, 'thought (incorrectly) it could handle', data.url);
                    continue;
                }
                ext = ext.replace(/\./gmi, '');
                return await processFinishedDownload(dl.url, `${data.relativeFile}.${ext}`, d.name);
            } catch (err) {
                if (err instanceof GracefulStopError) {
                    // Swallow graceful errors, because the user wants to exit cleanly.
                    console.debug("Graceful stop encountered in downloader:", d.name, err.message);
                } else {
                    console.error('Downloader Error:', d.name, data.url, isTest() ? err : '<snipped error trace>');
                }
            }
        }
    }

    if (!progress.shouldStop) {
        console.warn('Unable to find handler for:', dl.url.address);
        dl.url.handler = 'none';
        await dl.url.setFailed('Unable to find handler.');
    }
}


/**
 * Builds and saves a new DBFile for the given DBUrl and file path.
 */
export async function processFinishedDownload(url: DBUrl, subPath: string, handler: string) {
    url.file = buildFile(getAbsoluteDL(subPath), subPath);
    url.processed = true;
    url.failed = false;
    url.failureReason = null;
    url.completedUTC = Date.now();
    url.handler = handler;

    return url.save();
}
