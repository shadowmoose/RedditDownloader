import * as urlp from 'url';
import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {downloadMedia, getJSON} from "../../util/http";
import {DownloadProgress} from "../../util/state";
import * as ytdl from "../ytdl";
import path from "path";


const formatOpts = ["mp4", "webm", "webp", "largeGif"];

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
        const match = data.url.match(/\.com\/([a-zA-Z]+)/);
        const code = match ? match[1] : null;
        let api = await getJSON(`https://api.gfycat.com/v1/gfycats/${code}`).catch(err=>{});

        if (!api?.gfyItem?.content_urls) {
            api = await getJSON(`https://api.redgifs.com/v1/gfycats/${code}`)
        }

        if (!api?.gfyItem) {
            throw new Error('Could not find gfycat or redirected link.')
        }

        for (const f of formatOpts) {
            if (f in api.gfyItem.content_urls) {
                return downloadMedia(api.gfyItem.content_urls[f].url, data.file, progress);
            }
        }
    }
}
