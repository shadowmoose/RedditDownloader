import path from 'path';
import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {DownloadProgress} from "../../core/state";
import * as ytdl from '../ytdl';
import {isTest} from "../../core/config";


export default class YtdlDownloader extends Downloader {
    name: string = 'ytdl';

    protected async init(): Promise<any> {
        return ytdl.autoUpdate();
    }

    async getOrder(): Promise<number> {
        return 100;
    }

    async canHandle(data: DownloaderData): Promise<boolean> {
        return true;
    }

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress): Promise<string | void> {
        const fullPath = await ytdl.download(data.url, data.file, progress).catch(err => {
            if(!progress.shouldStop && isTest()) console.warn('YTDL Warning:', err)
        });
        return fullPath && path.extname(fullPath).replace(/^\./, '');
    }
}
