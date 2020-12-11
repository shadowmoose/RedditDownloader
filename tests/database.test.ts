import {makeDB} from "../src/database/db";
import DBSubmission from "../src/database/entities/db-submission";
import * as snoo from '../src/reddit/snoo';
import {getSavedPosts, getUpvoted} from "../src/reddit/snoo";
import DBFilter from "../src/database/entities/db-filter";
import DBSetting from "../src/database/entities/db-setting";
import DBSourceGroup from "../src/database/entities/db-source-group";
import DBSource from "../src/database/entities/db-source";
import DBDownload, {DownloadSubscriber} from "../src/database/entities/db-download";
import DBUrl from "../src/database/entities/db-url";


describe("Database Tests", () => {
    beforeEach(async () => {
        const conn = await makeDB();
        await conn.synchronize(true);  // Rerun sync to drop & recreate existing tables.
    });

    it("load specific submission", async () => {
        const t = await snoo.getSubmission('hrrh23');
        await t.save();
        expect(await DBSubmission.count()).toBeGreaterThan(0); // Stuff should be saved.
    });

    it('save multiple posts', async () => {
        const tst = getSavedPosts();

        while (true) {
            const nxt = await tst.next();
            if (nxt.done) break;

            await nxt.value.save();
        }
        expect(await DBSubmission.count()).toBeGreaterThan(0); // Stuff should be saved.
    });

    it('save upvoted posts', async () => {
        const tst = getUpvoted();

        while (true) {
            const nxt = await tst.next();
            if (nxt.done) break;

            await nxt.value.save();
        }
        expect(await DBSubmission.count()).toBeGreaterThan(0); // Stuff should be saved.
    });

    it('save filters', async () => {
        const sg = DBSourceGroup.build({color: "", id: 0, name: ""});

        for (let i = 0; i < 4; i++) {
            const f = DBFilter.build({
                comparator: ">",
                field: "title",
                forSubmissions: false,
                valueJSON: JSON.stringify(1000)
            });
            if (i === 1) f.value = 2000;
            (await sg.filters).push(f);
        }
        await sg.save();
        const filters = await DBFilter.find();
        const ids = new Set(filters.map(f => f.id));

        expect(ids.size).toBe(4);
        expect(filters.every(f=>f.value)).toBeTruthy();
        expect(filters[0].value).toBe(1000);
        expect(filters[1].value).toBe(2000);
    });

    it('save settings', async() => {
        expect(await DBSetting.get('test')).toBe(1337);  // Default value

        await DBSetting.set('test', 100);
        expect(await DBSetting.get('test')).toBe(100);  // Custom value

        const all = await DBSetting.getAll();
        expect(all.test).toBe(100);  // Full settings reload
    });

    it('save source group', async () => {
        const sg = DBSourceGroup.build({color: "", id: 0, name: "test-group"});
        const src = DBSource.build({dataJSON: "1337", id: 0, name: "test-source", type: 'test'});
        const fi = DBFilter.build({
            comparator: ">",
            field: "title",
            forSubmissions: false,
            valueJSON: JSON.stringify(1000)
        });
        (await sg.sources).push(src);
        (await sg.filters).push(fi);
        await sg.save();

        expect(await DBSourceGroup.findOne({id: 0})).toBeTruthy();
        expect(await DBFilter.findOne()).toBeTruthy();
        expect(await DBSource.findOne()).toBeTruthy();
    });

    it('submission get downloader', async () => {
        const sub = DBSubmission.buildTest();
        const dl = await DBDownload.getDownloader(sub, 'https://shadowmoo.se');
        (await sub.downloads).push(dl);
        await sub.save();

        expect(await DBSubmission.findOne()).toBeTruthy();
        expect(await DBDownload.findOne()).toBeTruthy();
        expect(await DBUrl.findOne()).toBeTruthy();

        const dl2 = await DBDownload.getDownloader(sub,'https://shadowmoo.se');
        expect(dl2.id).toEqual(dl.id); // Matching URL should return a clone of the original, completed DL.
        await dl2.save();

        const dl3 = await DBDownload.getDownloader(sub, 'https://shadowmoo.se', 'test-album-id');
        expect(dl3.id).not.toEqual(dl.id);  // Mismatching album should create a new DL in that album.
        expect(dl3.albumID).toEqual('test-album-id');
        expect(dl3.url.id).toEqual(dl.url.id);
        await dl3.save();
        
        expect(await DBDownload.count()).toEqual(2);
    });

    it('new urls trigger listener', async() => {
        const sub = DBSubmission.buildTest();
        const dl = await DBDownload.getDownloader(sub, 'https://shadowmoo.se');
        const dl2 = await DBDownload.getDownloader(sub, 'https://github.com');
        (await sub.downloads).push(dl);
        (await sub.downloads).push(dl2);
        const res = await Promise.all([
            DownloadSubscriber.awaitNew(),
            DownloadSubscriber.awaitNew(),
            sub.save()
        ]);
        expect(res[0]!.id).toEqual(dl.id);
        expect(res[1]!.id).toEqual(dl2.id);
    })
});
