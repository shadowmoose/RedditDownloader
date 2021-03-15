import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {DownloadProgress} from "../../util/state";
import axios from "axios";
import {getMediaMimeExtension, downloadMedia} from "../../util/http";

export class DirectDownloader extends Downloader {
    name: string = 'direct';

    async canHandle(data: DownloaderData): Promise<boolean> {
        const head = await axios.head(data.url);

        if (head.status !== 200) return false;

        return !!getMediaMimeExtension(head.headers['content-type']);
    }

    async getOrder(): Promise<number> {
        return 1;
    }

    protected async init(): Promise<any> {}

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress): Promise<string | void> {
        return downloadMedia(data.url, data.file, progress);
    }
}
