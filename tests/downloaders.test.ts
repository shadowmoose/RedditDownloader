import fs from "fs";
import * as ytdl from "../src/engine/downloaders/ytdl";
import { getAbsoluteDL } from '../src/engine/util/paths';
import {
    DownloaderData,
    DownloaderFunctions,
    getNextPendingDownload,
    handleDownload
} from "../src/engine/downloaders/downloaders";
import {DBPost, makeDB} from "../src/engine/database/db";
import DBSubmission from "../src/engine/database/entities/db-submission";
import DBDownload from "../src/engine/database/entities/db-download";
import {DownloadProgress} from "../src/engine/util/state";
import DBFile from "../src/engine/database/entities/db-file";
import {checkFFMPEGDownload, ffmpegPath, getFFMPEGVersion} from "../src/engine/downloaders/ffmpeg";
import {DirectDownloader} from "../src/engine/downloaders/wrappers/direct-downloader";
import {v4} from "uuid";
import {GracefulStopError} from "../src/engine/downloaders/wrappers/download-wrapper";
import {ImgurDownloader} from "../src/engine/downloaders/wrappers/imgur-downloader";

describe('YTDL Tests', () => {
    beforeAll( async() => {
        await ytdl.autoUpdate();
    });


    it('download from scratch', async() => {
        if (fs.existsSync(ytdl.exePath)) fs.unlinkSync(ytdl.exePath);

        const upd = await ytdl.autoUpdate();
        expect(fs.existsSync(ytdl.exePath)).toBeTruthy();
        expect(upd).toBeTruthy();
    });


    it('ffmpeg updates', async() => {
        await checkFFMPEGDownload();
        expect(fs.existsSync(ffmpegPath)).toBeTruthy();
        expect(await getFFMPEGVersion()).toBeTruthy();
    });


    it('skip when up to date', async() => {
        const upd = await ytdl.autoUpdate();
        expect(fs.existsSync(ytdl.exePath)).toBeTruthy();
        expect(upd).toBeFalsy();
    });


    it('download video', async() => {
        const dl = await ytdl.download('https://www.youtube.com/watch?v=q6EoRBvdVPQ', getAbsoluteDL('video'));

        expect(fs.existsSync(dl)).toBeTruthy();  // The resulting filename should have an extension added.
    });


    it('download audio', async() => {
        const dl = await ytdl.download('https://soundcloud.com/fiberjw/sausage', getAbsoluteDL('sausage'));

        expect(dl.endsWith('.mp3')).toBeTruthy();  // The resulting filename should have an extension added.
    });


    it('download gfycat', async() => {
        const dl = await ytdl.download('https://gfycat.com/impossibleveneratedhamadryad', getAbsoluteDL('gfy'));

        expect(dl.endsWith('.mp4')).toBeTruthy();  // The resulting filename should have an extension added.
    });


    it('invalid sites bubble errors', async() => {
        await expect(() => ytdl.download('https://shadowmoo.se', getAbsoluteDL('moose'))).rejects.toThrow();
    });
});


describe('Downloader Core Tests', () => {
    beforeEach(async () => {
        const conn = await makeDB();
        await conn.synchronize(true);  // Rerun sync to drop & recreate existing tables.
    });

    it('getNextPendingDownload works', async () => {
        const url = 'https://shadowmoo.se';
        const sub = DBSubmission.buildTest();
        const running = new Set<string>();
        expect(await getNextPendingDownload(running)).toBeFalsy();

        const dl = await DBDownload.getDownloader(sub, url, 'test-album-id');
        (await sub.downloads).push(dl);
        await sub.save();

        const pending = await getNextPendingDownload(running);
        expect(pending).toBeTruthy();
        expect(pending!.url.address).toEqual(url);

        running.add(url);
        expect(await getNextPendingDownload(running)).toBeFalsy();
    });

    it('handleDownload works', async() => {
        const sub = DBSubmission.buildTest();
        const dl = await DBDownload.getDownloader(sub, 'https://soundcloud.com/fiberjw/sausage');  // URL should be handled last, by YTDL.
        const prog = new DownloadProgress();
        (await sub.downloads).push(dl);
        await sub.save();

        const res = await handleDownload(dl, prog);
        if (!res) throw Error('Failed to handle test download');
        const file = await res.file;

        expect(res.processed).toBeTruthy();
        expect(res.completedUTC).toBeTruthy();
        expect(file).toBeTruthy();
        expect(fs.existsSync(getAbsoluteDL(file!.path))).toBeTruthy();
        expect(prog.handler).toEqual('ytdl');
        expect((await DBFile.findOne())?.path.endsWith('.mp3')).toBeTruthy(); // File is saved, with ext.
    });
});

/** Generate a mock DownloaderData object for testing. */
async function mockDownloadData(url: string): Promise<DownloaderData> {
    const post = DBSubmission.buildTest();
    const rnd = Math.random();

    return {
        relativeFile: `./${rnd}-test.file`,
        file: getAbsoluteDL(`./${rnd}-test.file`),
        url,
        post,
        dl: {} as any
    }
}

function mockDownloaderFunctions(): DownloaderFunctions {
    return {
        addAlbumURL: jest.fn(),
        markInvalid: jest.fn(),
        userExit: (reason?: string) => {throw new GracefulStopError(reason||'User exit')}
    };
}

describe('Direct Download Tests', () => {
    it('canHandle works', async () => {
        const dl = new DirectDownloader();
        expect(await dl.canHandle(await mockDownloadData('https://i.imgur.com/gYih4vd.jpg'))).toBeTruthy();
    })

    it('canHandle skips', async () => {
        const dl = new DirectDownloader();
        expect(await dl.canHandle(await mockDownloadData('https://google.com'))).toBeFalsy();
    })

    it('canHandle can error', async () => {
        const dl = new DirectDownloader();
        await expect(dl.canHandle(await mockDownloadData('http://127.0.0.1:49586'))).rejects.toThrow();
    })

    it('downloading works', async () => {
        const dat = await mockDownloadData('https://i.imgur.com/gYih4vd.jpg');
        const prog = new DownloadProgress();
        const dl = new DirectDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('jpg');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })

    it('downloading catches bad media url', async () => {
        const dat = await mockDownloadData('https://google.com');
        const prog = new DownloadProgress();
        const dl = new DirectDownloader();

        await expect(dl.download(dat, mockDownloaderFunctions(), prog)).rejects.toThrow();
    })
});


describe('Imgur Download Tests', () => {
    it('canHandle works', async () => {
        const dl = new ImgurDownloader();
        expect(await dl.canHandle(await mockDownloadData('https://i.imgur.com/gYih4vd.jpg'))).toBeTruthy();
        expect(await dl.canHandle(await mockDownloadData('https://imgur.com/gallery/plN58'))).toBeTruthy();
        expect(await dl.canHandle(await mockDownloadData('https://imgur.com.fake.com/'))).toBeFalsy();
        expect(await dl.canHandle(await mockDownloadData('https://fake-imgur.com/'))).toBeFalsy();
    })

    it('extracts gallery urls', async () => {
        const dl = new ImgurDownloader();
        const urls = await dl.extractAlbumLinks('plN58');

        if (!urls) throw Error('Failed to find gallery URLs.');

        expect(urls?.length).toEqual(134);

        for (const u of urls) {
            expect(u).toMatch(/\/\w{7}\.\w{3}$/)  // Ends with "/filename.ext".
        }
    })

    it('invalid gallery', async () => {
        const dl = new ImgurDownloader();
        const urls = await dl.extractAlbumLinks('awerasfe');

        expect(urls).toBeFalsy();
    })

    it('API gallery', async () => {
        const dl = new ImgurDownloader();
        const urls = await dl.extractAlbumAPI('plN58');

        expect(urls.length).toEqual(134);
        expect(urls[0]).toBeTruthy();
    })

    it('download gallery', async () => {
        const dat = await mockDownloadData('https://imgur.com/gallery/plN58');
        const prog = new DownloadProgress();
        const funcs: any = mockDownloaderFunctions();
        const dl = new ImgurDownloader();
        const res = await dl.download(dat, funcs, prog);

        expect(funcs.addAlbumURL.mock.calls.length).toEqual(134);
        expect(res).toBeFalsy();
        expect(prog.percent).toEqual(0);
    })

    it('download direct image', async () => {
        const dat = await mockDownloadData('https://i.imgur.com/gYih4vd.jpg');
        const prog = new DownloadProgress();
        const dl = new ImgurDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('jpg');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })

    it('download gif as mp4', async () => {
        const dat = await mockDownloadData('imgur.com/r/gifs/jIuIbIu');  // Leave off ext to test full flow.
        const prog = new DownloadProgress();
        const dl = new ImgurDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('mp4');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })
});
