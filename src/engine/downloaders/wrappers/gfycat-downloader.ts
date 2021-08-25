import * as urlp from 'url';
import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {downloadMedia, getJSON} from "../../util/http";
import {DownloadProgress} from "../../util/state";
import * as ytdl from "../ytdl";
import path from "path";
import {isTest} from "../../util/config";


const formatOpts = ["mp4Url", "mp4", "webm", "webp", "largeGif"];

export class GfycatDownloader extends Downloader {
    name: string = 'gfycat';

    async canHandle(data: DownloaderData): Promise<boolean> {
        return !!urlp.parse(data.url).hostname?.match(/^gfycat\.com$|.*\.gfycat\.com$|^redgifs\.com$|.*\.redgifs\.com$/)
    }

    async getOrder(): Promise<number> {
        return 0;
    }

    protected async init(): Promise<any> {
        return ytdl.autoUpdate();
    }

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress) {
        const match = urlp.parse(data.url).path;
        const code = match ? path.basename(match).split('.')[0].split('-')[0] : null;
        let api = await getJSON(`https://api.gfycat.com/v1/gfycats/${code}`).catch(_err=>{});

        progress.status = 'Searching gfycat for media...';

        if (!(api?.gfyItem?.content_urls)) {
            api = await getJSON(`https://api.redgifs.com/v1/gfycats/${code?.toLowerCase()}`).catch(_err=>{})
        }

        if (!(api?.gfyItem)) {
            return actions.markInvalid('Could not find gfycat or redirected link: ' + code);
        }

        for (const f of formatOpts) {
            // Some fields are within the direct obj, but the backups are within the "content_urls" section.
            const val = api.gfyItem.content_urls[f] ? api.gfyItem.content_urls[f].url : (f in api.gfyItem) ? api.gfyItem[f] : null;
            if (val) {
                progress.status = 'Downloading from gfycat.';

                return downloadMedia(val, data.file, progress).catch(err => {
                    if (isTest()) console.error(err);
                    return actions.markInvalid('Failed to download valid media file: ' + f);
                });
            }
        }
        return actions.markInvalid('Failed to locate a valid file type.')
    }
}
