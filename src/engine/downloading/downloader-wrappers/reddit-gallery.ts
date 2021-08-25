import * as urlp from 'url';
import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {DownloadProgress} from "../../core/state";
import * as http from "../../util/http";
import * as snoo from "../../reddit/snoo";
import * as ps from '../../reddit/pushshift';


export class RedditGalleryDownloader extends Downloader {
    name: string = 'reddit-gallery';

    async canHandle(data: DownloaderData): Promise<boolean> {
        const host = urlp.parse(data.url).hostname;
        const path = urlp.parse(data.url).path;
        return Boolean(host?.match(/^reddit\.com$|.*\.reddit\.com$/)) && Boolean(path?.match(/\/gallery\//));
    }

    async getOrder(): Promise<number> {
        return 0;
    }

    protected async init(): Promise<any> {}

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress): Promise<string | void> {
        // Album download:
        const match = data.url.match(/gallery\/(\w+)/);
        const submissionID = match ? 't3_' + match[1] : null;

        if (!submissionID) return;

        const sub = await snoo.getSubmission(submissionID).catch(()=>null) || await ps.getSubmission(submissionID);

        if (sub) {
            const post = sub.loadedData;
            // @ts-ignore
            const meta: Record<any, any> = await post.media_metadata;
            // @ts-ignore
            const galleryData: any = await post.gallery_data;
            const ret: string[] = [];

            if (!meta || !galleryData.items) {
                return actions.markInvalid('Failed to locate the expected gallery property in Submission.');
            }

            progress.status = 'Extracting reddit album URLs...';

            const gKeys: string[] = galleryData.items.map((gd: any) => gd.media_id);

            for (const k of gKeys) {
                const m = meta[k];
                Object.values(m).forEach((s: any) => {
                    if (!s.x || !s.y) return;
                    const url: any = Object.values(s).find(v => `${v}`.startsWith('http'));
                    if (url) ret.push(url);
                });
            }

            if (!ret.length) {
                return actions.markInvalid('Failed to extract any URLS from Submission Album.');
            }

            await actions.addAlbumUrls(ret);
            return;
        } else {
            return actions.markInvalid('Failed to locate album Submission.');
        }
    }
}
