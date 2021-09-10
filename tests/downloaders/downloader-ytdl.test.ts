import * as ytdl from "../../src/engine/downloading/ytdl";
import fs from "fs";
import {
    checkFFMPEGDownload,
    ffmpegPath,
    ffprobePath, fileHasAudio,
    getFFMPEGVersion,
    getFFProbeVersion, getMediaMetadata
} from "../../src/engine/file-processing/ffmpeg";
import {getAbsoluteDL} from "../../src/engine/core/paths";
import {mockDownloadData, mockDownloaderFunctions} from "./test-util";
import {DownloadProgress} from "../../src/engine/core/state";
import YtdlDownloader from "../../src/engine/downloading/downloader-wrappers/ytdl-downloader";
import {getLatestVersion, getLocalVersion} from "../../src/engine/downloading/ytdl";


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


    it('ffprobe updates', async() => {
        await checkFFMPEGDownload();
        expect(fs.existsSync(ffprobePath())).toBeTruthy();
        expect(await getFFProbeVersion()).toBeTruthy();
    });


    it('ffprobe audio check fails gracefully', async() => {
        expect(await fileHasAudio('./fake-file.txt')).toBe(false);
    });


    it('skip when up to date', async() => {
        console.log(ytdl.exePath, await getLocalVersion(), await getLatestVersion());

        expect(fs.existsSync(ytdl.exePath)).toBeTruthy();
        const upd = await ytdl.autoUpdate();
        expect(fs.existsSync(ytdl.exePath)).toBeTruthy();
        expect(upd).toBeFalsy();

        const local = await getLocalVersion();
        expect(local).toBeTruthy();
        expect(local).toEqual(await getLatestVersion());
    });


    it('download video', async() => {
        const dl = await ytdl.download('https://www.youtube.com/watch?v=q6EoRBvdVPQ', getAbsoluteDL('video'));

        expect(fs.existsSync(dl)).toBeTruthy();  // The resulting filename should have an extension added.

        const metadata = await getMediaMetadata(dl);
        expect(metadata.duration).toBe(9.021);
        expect(metadata.width).toBe(480);
        expect(metadata.height).toBe(360);
        expect(metadata.bitrate).toBeTruthy();
        expect(metadata.audioCodec).toBeTruthy();
        expect(metadata.videoCodec).toBeTruthy();
    });


    it('download audio', async() => {
        const dl = await ytdl.download('https://soundcloud.com/fiberjw/sausage', getAbsoluteDL('sausage'));

        expect(dl.endsWith('.mp3')).toBeTruthy();  // The resulting filename should have an extension added.
        expect(await fileHasAudio(dl)).toBe(true);

        const metadata = await getMediaMetadata(dl);
        expect(metadata.duration).toBe(20.610612);
        expect(metadata.width).toBe(null);
        expect(metadata.height).toBe(null);
        expect(metadata.bitrate).toBeTruthy();
        expect(metadata.audioCodec).toBeTruthy();
        expect(metadata.videoCodec).toBeFalsy();
    });


    it('download gfycat', async() => {
        const dl = await ytdl.download('https://gfycat.com/impossibleveneratedhamadryad', getAbsoluteDL('gfy'));

        expect(dl.endsWith('.mp4')).toBeTruthy();  // The resulting filename should have an extension added.
        expect(await fileHasAudio(dl)).toBe(false);

        const metadata = await getMediaMetadata(dl);
        expect(metadata.duration).toBe(1.4);
        expect(metadata.width).toBe(218);
        expect(metadata.height).toBe(208);
        expect(metadata.bitrate).toBeTruthy();
        expect(metadata.audioCodec).toBeFalsy();
        expect(metadata.videoCodec).toBeTruthy();
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
        expect(res).toEqual('webm');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    });

    it('download can fail', async () => {
        const dat = await mockDownloadData('https://shadowmoo.se');
        const prog = new DownloadProgress(0);
        const dl = new YtdlDownloader();

        await expect(await dl.download(dat, mockDownloaderFunctions(), prog)).toBeFalsy();
    });
});
