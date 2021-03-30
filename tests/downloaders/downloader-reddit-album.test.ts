import {mockDownloadData, mockDownloaderFunctions} from "./test-util";
import {DownloadProgress} from "../../src/engine/util/state";
import {RedditGalleryDownloader} from "../../src/engine/downloaders/wrappers/reddit-gallery";


describe('Reddit Album Download Tests', () => {
    it('canHandle works', async () => {
        const dl = new RedditGalleryDownloader();
        expect(await dl.canHandle(await mockDownloadData('https://www.reddit.com/gallery/hrrh23'))).toBeTruthy();
        expect(await dl.canHandle(await mockDownloadData('https://reddit.com.fake.com/'))).toBeFalsy();
        expect(await dl.canHandle(await mockDownloadData('https://gallery.reddit.com/'))).toBeFalsy();
    });


    it('download gallery', async () => {
        const dat = await mockDownloadData('https://www.reddit.com/gallery/hrrh23');
        const prog = new DownloadProgress(0);
        const funcs: any = mockDownloaderFunctions();
        const dl = new RedditGalleryDownloader();
        const res = await dl.download(dat, funcs, prog);

        expect(funcs.addAlbumUrls.mock.calls.length).toEqual(1);
        expect(res).toBeFalsy();
        expect(prog.percent).toEqual(0);

        const urls = funcs.addAlbumUrls.mock.calls[0][0];
        expect(urls.length).toEqual(3);
        for (const u of urls) {
            expect(u).toContain('512'); // Found largest resolution.
        }
    })

    it('invalid gallery', async () => {
        const dat = await mockDownloadData('https://www.reddit.com/gallery/hrrh__');
        const prog = new DownloadProgress(0);
        const funcs: any = mockDownloaderFunctions();
        const dl = new RedditGalleryDownloader();

        await expect(dl.download(dat, funcs, prog)).rejects.toThrow();
    })
})
