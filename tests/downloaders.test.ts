import fs from "fs";
import * as ytdl from "../src/downloaders/ytdl";
import { getAbsoluteDL } from '../src/util/paths';
import {downloadFFMPEG} from "../src/downloaders/ytdl";
import {getNextPendingDownload, handleDownload} from "../src/downloaders";
import {makeDB} from "../src/database/db";
import DBSubmission from "../src/database/entities/db-submission";
import DBDownload from "../src/database/entities/db-download";
import {DownloadProgress} from "../src/util/state";
import DBFile from "../src/database/entities/db-file";

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
        const res = await downloadFFMPEG();
        expect(fs.existsSync(res)).toBeTruthy();
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
        const dl = await DBDownload.getDownloader(sub, 'https://soundcloud.com/fiberjw/sausage');
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
        expect((await DBFile.findOne())?.path.endsWith('.mp3')).toBeTruthy(); // File is saved, with ext.
    });
});
