import * as ytdl from "../../src/engine/downloaders/ytdl";
import {GfycatDownloader} from "../../src/engine/downloaders/wrappers/gfycat-downloader";
import {DownloadProgress} from "../../src/engine/util/state";
import {mockDownloadData, mockDownloaderFunctions} from "./test-util";


describe('Gfycat Download Tests', () => {
    beforeAll( async() => {
        await ytdl.autoUpdate();
    });

    it('canHandle works', async () => {
        const dl = new GfycatDownloader();
        expect(await dl.canHandle(await mockDownloadData('https://gfycat.com/kaleidoscopicnauticalbordercollie'))).toBeTruthy();
    })

    it('canHandle skips', async () => {
        const dl = new GfycatDownloader();
        expect(await dl.canHandle(await mockDownloadData('https://fake-gfycat.com/testvalue'))).toBeFalsy();
    })

    it('download with CDN redirect', async () => {
        const dat = await mockDownloadData('https://gfycat.com/kaleidoscopicnauticalbordercollie');
        const prog = new DownloadProgress(0);
        const dl = new GfycatDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('mp4');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })

    it('download directly', async () => {
        const dat = await mockDownloadData('https://gfycat.com/densepepperyfennecfox-overthinking-overthink-headache-thought-painful');
        const prog = new DownloadProgress(0);
        const dl = new GfycatDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toBeTruthy();
        expect(res).toEqual('mp4');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })

    it('download can fail', async () => {
        const dat = await mockDownloadData('https://gfycat.com/thisIsAFakeId');
        const prog = new DownloadProgress(0);
        const dl = new GfycatDownloader();

        await expect(dl.download(dat, mockDownloaderFunctions(), prog)).rejects.toThrow();
    })
});
