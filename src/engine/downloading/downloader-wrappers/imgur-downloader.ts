import * as urlp from 'url';
import Downloader from "./download-wrapper";
import {DownloaderData, DownloaderFunctions} from "../downloaders";
import {DownloadProgress} from "../../core/state";
import * as http from "../../util/http";
import path from 'path';
import DBSetting from "../../database/entities/db-setting";
import {isTest} from "../../core/config";
const imgur = require('imgur');

export class ImgurDownloader extends Downloader {
    name: string = 'imgur';

    async canHandle(data: DownloaderData): Promise<boolean> {
        return !!urlp.parse(data.url).hostname?.match(/^imgur\.com$|.*\.imgur\.com$/)
    }

    async getOrder(): Promise<number> {
        return 0;
    }

    protected async init(): Promise<any> {}

    isAlbum(url: string) {
        const path = urlp.parse(url).path;
        return ['/a/', '/gallery/'].some(p => path?.startsWith(p));
    }

    /**
     * Probes the given imgur url and figures out the best path to directly download the image, if possible.
     * @param url
     */
    async buildDirectURL(url: string) {
        const parsed = urlp.parse(url);
        const upth = parsed.path || '';
        let ext = path.extname(upth);
        const file = path.basename(upth).replace(ext, '');

        if (!ext) {
            const dat = await http.getMimeType(`https://i.imgur.com/${file}.png`);  // imgur ignores bad extension.
            ext = dat.ext ? '.'+dat.ext : ext;
        }

        if (['mp4', 'webm', 'gif', 'gifv'].some(e=>ext.endsWith(e))) ext = '.mp4';
        return `https://i.imgur.com/${file}${ext}`;
    }

    async extractAlbumLinks(albumKey: string) {
        try {
            const dat: string = await http.getRaw(`https://imgur.com/a/${albumKey}/layout/blog`);

            const regex1 = RegExp('.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\\.[a-zA-Z0-9]+)".*?', 'gmi');
            let m: any;
            const found = new Set<string>();
            while ((m = regex1.exec(dat)) !== null) {
                found.add(`https://i.imgur.com/${m[1]}${m[2]}`);
            }
            return Array.from(found);
        } catch (err) {
            return null;
        }
    }

    /** use the imgur API to extract album URLs. May be throttled. */
    async extractAlbumUsingAPI(albumKey: string): Promise<string[]> {
        const id = await DBSetting.get('imgurClientId');
        imgur.setClientId(id);

        return imgur
            .getAlbumInfo(albumKey)
            .then((json: any) => {
                return json.images.map((im: any) => im.link);
            })
            .catch((err: any) => {
                if (isTest()) console.error(err);
                return [];
            });
    }

    async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress): Promise<string | void> {
        if (!this.isAlbum(data.url)) {
            progress.status = 'Downloading from imgur.';
            try {
                return await http.downloadMedia(await this.buildDirectURL(data.url), data.file, progress);
            } catch (err) {
                if (isTest()) console.error(err);
                if (progress.shouldStop) return;
                return actions.markInvalid('Failed to download non-album image.')
            }
        } else {
            // Album download:
            const match = data.url.match(/(https?):\/\/(www\.)?(?:m\.)?imgur\.com\/(a|gallery)\/([a-zA-Z0-9]+)(#[0-9]+)?/);
            const albumKey = match ? match[4] : null;

            if (!albumKey) return actions.markInvalid('Failed to extract album key from URL.');

            progress.status = 'Extracting imgur album URLs...';

            let urls: string[] = [];
            const found = await this.extractAlbumLinks(albumKey);

            if (found && found.length) {
                urls = urls.concat(found);
            } else {
                urls = urls.concat(await this.extractAlbumUsingAPI(albumKey));
            }

            if (urls.length) {
                await actions.addAlbumUrls(urls).catch(err => {
                    console.log('Imgur album error...');
                    console.error(err);
                });
                return;
            } else {
                return actions.markInvalid('Failed to extract valid URLS from album.');
            }
        }
    }
}
