import * as gen from '../src/util/name-generator'
import {getComment, getSubmission} from "../src/reddit/snoo";
import DBDownload from "../src/database/entities/db-download";
import {makeDB} from "../src/database/db";
import {getAbsoluteDL} from "../src/util/paths";
import {MAX_NAME_LEN} from "../src/util/name-generator";
import DBUrl from "../src/database/entities/db-url";
import DBFile from "../src/database/entities/db-file";

describe('Name Generator Tests', () => {
    beforeEach(async () => {
        const conn = await makeDB();
        await conn.synchronize(true);  // Rerun sync to drop & recreate existing tables.
    });

    it('simple name works', async() => {
        const template = '[subreddit]/[author]/[type]s/[title]';
        const output = gen.makePathFit({
            author: "ShadowMoose",
            createdUTC: 0,
            id: "t3_test",
            over18: false,
            score: 1337,
            subreddit: "test_sub",
            title: "This is a test title.",
            type: 'submission',
            url: ""
        }, template)

        expect(output).toEqual('test_sub/ShadowMoose/submissions/This is a test title_');
    })

    it(`nested brackets pass through`, async() => {
        const template = '[subreddit]/[author]/[type]s/[title]';
        const output = gen.makePathFit({
            author: "[ShadowMoose]",
            createdUTC: 0,
            id: "t3_test",
            over18: false,
            score: 1337,
            subreddit: "test_sub",
            title: "This is a test [title].",
            type: 'comment',
            url: ""
        }, template)

        expect(output).toEqual('test_sub/[ShadowMoose]/comments/This is a test [title]_');
    });

    it(`long names condense`, async() => {
        const template = '[subreddit]/[author]/[type]s/[title]';
        const output = gen.makePathFit({
            author: "[ShadowMoose]",
            createdUTC: 0,
            id: "t3_test",
            over18: false,
            score: 1337,
            subreddit: "test_sub",
            title: "This is a test [title].".repeat(100),
            type: 'comment',
            url: ""
        }, template)

        expect(getAbsoluteDL(output).length).toBeLessThan(MAX_NAME_LEN+1);
    });

    it('generate for real comment', async () => {
        const c = await getComment('c0b7g40');
        const dl = DBDownload.build({
            albumID: "test",
            isAlbumParent: false,
            url: await DBUrl.dedupeURL('test.com')
        });
        (await c.downloads).push(dl);
        await c.save();
        const path = await gen.makeName(dl, '[subreddit]/[author]/[type]s/[title]')
        expect(path).toBe('pics/randomredditor/comments/test post please ignore');
    });

    it('generate for real submission', async () => {
        const c = await getSubmission('hrrh23');
        const dl = DBDownload.build({
            albumID: "test",
            isAlbumParent: false,
            url: await DBUrl.dedupeURL('test.com')
        });
        (await c.downloads).push(dl);
        await c.save();
        const path = await gen.makeName(dl, '[subreddit]/[author]/[type]s/[title]')
        expect(path).toBe('announcements/LanterneRougeOG/submissions/Now you can make posts with multiple images_');
    });

    it('generate incremented filenames', async () => {
        const c = await getSubmission('hrrh23');
        const dl = DBDownload.build({
            albumID: "test",
            isAlbumParent: false,
            url: await DBUrl.dedupeURL('test.com')
        });
        (await c.downloads).push(dl);
        await c.save();
        const path = await gen.makeName(dl, '[subreddit]/[author]/[type]s/[title]')
        expect(path).toBe('announcements/LanterneRougeOG/submissions/Now you can make posts with multiple images_');

        // Save so the generator finds a duplicate:
        await DBFile.build({
            dHash: null, hash1: null, hash2: null, hash3: null, hash4: null,
            mimeType: "",
            path,
            shaHash: "",
            size: 0,
        }).save();

        const p2 = await gen.makeName(dl, '[subreddit]/[author]/[type]s/[title]')
        expect(p2).toBe('announcements/LanterneRougeOG/submissions/Now you can make posts with multiple images_ - 2');
    });
});
