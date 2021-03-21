import * as ytdl from "../../src/engine/downloaders/ytdl";
import fs from "fs";
import {checkFFMPEGDownload, ffmpegPath, getFFMPEGVersion} from "../../src/engine/downloaders/ffmpeg";
import {getAbsoluteDL} from "../../src/engine/util/paths";
import {mockDownloadData, mockDownloaderFunctions} from "./test-util";
import {DownloadProgress} from "../../src/engine/util/state";
import YtdlDownloader from "../../src/engine/downloaders/wrappers/ytdl-downloader";


describe('YTDL Library Tests', () => {
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
        expect(fs.existsSync(ffmpegPath())).toBeTruthy();
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


describe('YTDL Downloader Tests', () => {
    beforeAll( async() => {
        await ytdl.autoUpdate();
    });

    it('download youtube', async () => {
        const dat = await mockDownloadData('https://www.youtube.com/watch?v=q6EoRBvdVPQ');
        const prog = new DownloadProgress(0);
        const dl = new YtdlDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('mkv');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })

    it('download can fail', async () => {
        const dat = await mockDownloadData('https://shadowmoo.se');
        const prog = new DownloadProgress(0);
        const dl = new YtdlDownloader();

        await expect(dl.download(dat, mockDownloaderFunctions(), prog)).rejects.toThrow();
    })
});
