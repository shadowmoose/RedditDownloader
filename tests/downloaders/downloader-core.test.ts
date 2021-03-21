import fs from "fs";
import * as ytdl from "../../src/engine/downloaders/ytdl";
import {getAbsoluteDL} from '../../src/engine/util/paths';
import {getNextPendingDownload, handleDownload} from "../../src/engine/downloaders/downloaders";
import {makeDB} from "../../src/engine/database/db";
import DBSubmission from "../../src/engine/database/entities/db-submission";
import DBDownload from "../../src/engine/database/entities/db-download";
import {DownloadProgress} from "../../src/engine/util/state";
import DBFile from "../../src/engine/database/entities/db-file";


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
        const prog = new DownloadProgress(0);
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
        expect(prog.percent).toEqual(1);
        expect((await DBFile.findOne())?.path.endsWith('.mp3')).toBeTruthy(); // File is saved, with ext.
    });
});

