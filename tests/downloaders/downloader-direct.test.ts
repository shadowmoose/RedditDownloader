import {DirectDownloader} from "../../src/engine/downloading/downloader-wrappers/direct-downloader";
import {DownloadProgress} from "../../src/engine/core/state";
import {mockDownloadData, mockDownloaderFunctions} from "./test-util";


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
        await expect(await dl.canHandle(await mockDownloadData('http://127.0.0.1:49586'))).toBeFalsy();
    })

    it('downloading works', async () => {
        const dat = await mockDownloadData('https://i.imgur.com/gYih4vd.jpg');
        const prog = new DownloadProgress(0);
        const dl = new DirectDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('jpg');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })

    it('downloading catches bad media url', async () => {
        const dat = await mockDownloadData('https://google.com');
        const prog = new DownloadProgress(0);
        const dl = new DirectDownloader();

        await expect(await dl.download(dat, mockDownloaderFunctions(), prog)).toBeFalsy();
    })
});
