import path from 'path';
import Downloader from "../downloader";
import {DownloaderData, DownloaderFunctions} from "../index";
import {DownloadProgress} from "../../util/state";
import * as ytdl from '../ytdl';

export default class YtdlDownloader extends Downloader {
    name: string = 'ytdl';

    protected async init(): Promise<any> {
        return ytdl.autoUpdate();
    }

    async getOrder(): Promise<number> {
        return 0;
    }

    async canHandle(data: DownloaderData): Promise<boolean> {
        return true;
    }

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress): Promise<string | void> {
        const fullPath = await ytdl.download(data.url, data.file, progress);
        return path.extname(fullPath);
    }
}
