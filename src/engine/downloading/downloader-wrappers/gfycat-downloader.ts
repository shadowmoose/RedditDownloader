import * as urlp from 'url';
import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {downloadMedia, getJSON} from "../../util/http";
import {DownloadProgress} from "../../core/state";
import * as ytdl from "../ytdl";
import path from "path";
import {isTest} from "../../core/config";


const formatOpts = ["mp4Url", "mp4", "webm", "webp", "largeGif", "mobile"];

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

    async handleUser(progress: DownloadProgress, actions: DownloaderFunctions, username: string, ogHost: string) {
        const possibleUrls = [
            `https://api.gfycat.com/v1/users/${username}/gfycats`,
            `https://api.redgifs.com/v1/users/${username}/gfycats`
        ].sort((a, b) => {
            // Prioritize URLs which match the original link. The user may have migrated, so still try them all.
            let aa = a.includes(ogHost.replace('www.', '')) ? 1 : 0;
            let bb = b.includes(ogHost.replace('www.', '')) ? 1 : 0;
            return bb - aa;
        });

        progress.status = `Searching for user's ${username} content.`;

        for (const u of possibleUrls) {
            const allFound: string[] = [];
            let api: any;

            do {
                api = await getJSON(u, {
                    count: '100',
                    cursor: api?.cursor || undefined
                }).catch(_err=>{});
                if (!api) break;

                const found: string[] = api.gfycats.map((gfy: any) => {
                    for (const f of formatOpts) {
                        const link = gfy.content_urls[f];

                        if (link) return link.url;
                    }
                }).filter((f: string)=>!!f);

                allFound.push(...found);
            } while (api?.cursor);

            if (allFound.length) {
                return await actions.addAlbumUrls(allFound);
            }
        }

        return await actions.markInvalid(`Unable to locate user profile data: ${username}`);
    }

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress) {
        const parsedUrl = urlp.parse(data.url)
        const match = parsedUrl.path;

        if (match && (match?.includes('/users/') || match.includes('@'))) {
            const username = match.includes('@') ?
                match.split('@')[1].split('/')[0] : match.split('/users/')[1].split('/')[0];
            return this.handleUser(progress, actions, username, `${parsedUrl.hostname}`);
        }

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
                    if (progress.shouldStop) return;
                    return actions.markInvalid('Failed to download valid media file: ' + f);
                });
            }
        }
        if (progress.shouldStop) return;
        return actions.markInvalid('Failed to locate a valid file type.')
    }
}
