import {DownloaderData, DownloaderFunctions} from "../../src/engine/downloading/downloaders";
import DBSubmission from "../../src/engine/database/entities/db-submission";
import {getAbsoluteDL} from "../../src/engine/core/paths";
import {GracefulStopError, InvalidDownloaderError} from "../../src/engine/downloading/downloader-wrappers/download-wrapper";

/** Generate a mock DownloaderData object for testing. */
export async function mockDownloadData(url: string): Promise<DownloaderData> {
    const post = DBSubmission.buildTest();
    const rnd = Math.random();

    return {
        relativeFile: `./${rnd}-test.file`,
        file: getAbsoluteDL(`./${rnd}-test.file`),
        url,
        post,
        dl: {} as any
    }
}

export function mockDownloaderFunctions(): DownloaderFunctions {
    return {
        addAlbumUrls: jest.fn((..._p: any) => Promise.resolve()),
        markInvalid: (reason: string) => {
            throw new InvalidDownloaderError(reason);
        },
        userExit: (reason?: string) => {
            throw new GracefulStopError(reason || 'User exit')
        }
    };
}
