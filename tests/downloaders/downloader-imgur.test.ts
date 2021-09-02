import {ImgurDownloader} from "../../src/engine/downloading/downloader-wrappers/imgur-downloader";
import {DownloadProgress} from "../../src/engine/core/state";
import {mockDownloadData, mockDownloaderFunctions} from "./test-util";
import {downloadFFProbe, getMediaMetadata} from "../../src/engine/file-processing/ffmpeg";


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
        const urls = await dl.extractAlbumUsingAPI('plN58');

        expect(urls.length).toEqual(134);
        expect(urls[0]).toBeTruthy();
    })

    it('download gallery', async () => {
        const dat = await mockDownloadData('https://imgur.com/gallery/plN58');
        const prog = new DownloadProgress(0);
        const funcs: any = mockDownloaderFunctions();
        const dl = new ImgurDownloader();
        const res = await dl.download(dat, funcs, prog);

        expect(funcs.addAlbumUrls.mock.calls.length).toEqual(1);
        expect(res).toBeFalsy();
        expect(prog.percent).toEqual(0);
    })

    it('download direct image', async () => {
        const dat = await mockDownloadData('https://i.imgur.com/gYih4vd.jpg');
        const prog = new DownloadProgress(0);
        const dl = new ImgurDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toEqual('jpg');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.

        await downloadFFProbe();
        const metadata = await getMediaMetadata(dat.file +'.'+ res);
        expect(metadata.width).toBe(1025);
        expect(metadata.height).toBe(1025);
    })

    it('download gif as mp4', async () => {
        const dat = await mockDownloadData('imgur.com/r/gifs/jIuIbIu');  // Leave off ext to test full flow.
        const prog = new DownloadProgress(0);
        const dl = new ImgurDownloader();

        const res = await dl.download(dat, mockDownloaderFunctions(), prog);
        expect(res).toEqual('mp4');
        expect(prog.percent).toEqual(1);  // Download completes in progress tracker.
    })
});
