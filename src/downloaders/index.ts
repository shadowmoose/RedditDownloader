import {buildFile} from "./dl-file-processing";
import DBDownload, {DownloadSubscriber} from "../database/entities/db-download";
import promisePool, {mutex} from "../util/promise-pool";
import DBSetting from "../database/entities/db-setting";
import {makeName} from "../util/name-generator";
import {DBPost} from "../database/db";
import DBUrl from "../database/entities/db-url";
import Downloader, {GracefulStopError} from "./downloader";
import {v4} from "uuid";
import {DownloaderState, DownloadProgress} from "../util/state";
import YtdlDownloader from "./wrappers/ytdl-downloader";
import {getAbsoluteDL} from "../util/paths";


export async function getDownloaders(): Promise<Downloader[]> {
    const list = [new YtdlDownloader()];

    for (const l of list) {
        await l.initOnce();
        l.order = await l.getOrder();
    }

    return list.sort((a, b) => a.order - b.order);
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
        query = query.andWhere("url.address NOT IN (:addrs)", {addrs: Array.from(ignoreURLs)});
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
            const dlp = new DownloadProgress();
            state.activeDownloads[threadNumber] = dlp;
            await handleDownload(nxt, dlp);
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
    /** The relative path of this file. Not as useful for Downloaders. */
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
    /** Register a new URL, and sets the current URL as an album parent. Noop for nested albums. */
    addAlbum: (url: string) => Promise<DBDownload|null>;
    /** Mark the current URL as failed, and add a reason. The URL will be skipped by default after this. */
    markInvalid: (reason: string) => Promise<DBUrl>;
    /** gracefully exit in a way that will be swallowed by the parent error handling. */
    userExit: (reason?: string) => void;
}

/**
 * Generate the data structure and callbacks that are to be passed into the Downloader instances.
 */
export async function buildDownloadData(dl: DBDownload) {
    const relativeFile = await makeName(dl, await DBSetting.get('outputTemplate'));
    const data: DownloaderData = {
        relativeFile,
        file: getAbsoluteDL(relativeFile),
        url: dl.url.address,
        post: await dl.getDBParent(),
        dl
    };
    const callbacks: DownloaderFunctions = {
        addAlbum: async (url: string) => {
            if (dl.albumID && !dl.isAlbumParent) return null;  // Disallow nested albums.
            dl.albumID = v4();
            dl.isAlbumParent = true;
            dl.url.processed = true;
            await dl.save();
            return (await DBDownload.getDownloader(data.post, url, dl.albumID)).save();
        },
        markInvalid: async (reason: string) => {
            dl.url.processed = true;
            dl.url.failed = true;
            dl.url.failureReason = reason;
            return dl.url.save();
        },
        userExit: (reason?: string) => {throw new GracefulStopError(reason||'User exit')}
    };

    return {data, callbacks};
}

/**
 * Iterate through all available downloaders, attempting to handle the given DBDownload.
 */
export async function handleDownload(dl: DBDownload, progress: DownloadProgress) {
    const {data, callbacks} = await buildDownloadData(dl);

    for (const d of await getDownloaders()) {
        if (progress.shouldStop || dl.url.processed) break;
        progress.status = `Looking for downloaders to handle this URL...`;
        if (await d.canHandle(data)) {
            progress.handler = d.name;
            progress.status = `Downloading the URL...`;
            progress.knowsPercent = false;
            progress.percent = 0;

            try {
                let ext = await d.download(data, callbacks, progress);
                if (!ext) {
                    console.warn('handler:', d.name, 'thought (incorrectly) it could handle', data.url);
                    continue;
                }
                ext = ext.replace(/\./gmi, '');
                console.log("Downloaded file:", ext);
                return await processFinishedDownload(dl.url, `${data.relativeFile}.${ext}`, d.name);
            } catch (err) {
                if (err instanceof GracefulStopError) {
                    // Swallow graceful errors, because the user wants to exit cleanly.
                    console.debug("Graceful stop encountered in downloader:", d.name, err.message);
                } else {
                    console.error(err);
                }
            }
        }
    }
    console.warn('Unable to find handler for:', dl.url.address);
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
