import {DownloaderData, DownloaderFunctions} from "./index";
import {DownloadProgress} from "../util/state";


export default abstract class Downloader {
    public order: number = 0;
    private initPromise: Promise<any>|null = null;
    abstract name: string;

    /** Run this Downloader's init function once, and/or await for that single call to finish. */
    public async initOnce() {
        return this.initPromise = this.initPromise || this.init();
    }

    /** Perform any initial setup this Downloader may require. Only ever called once. */
    protected abstract async init(): Promise<any>;

    /** If this Downloader thinks that it can successfully download the given URL Data. */
    abstract async canHandle(data: DownloaderData): Promise<boolean>;

    /** Get the user-specified order that this Downloader should run in. */
    abstract async getOrder(): Promise<number>;

    /**
     * Attempts to download using this Downloader. If successful, returns the file extension that is now saved.
     */
    abstract async download(data: DownloaderData, actions: DownloaderFunctions, progress: DownloadProgress): Promise<string|void>;
}


export class GracefulStopError extends Error {
    constructor(message: string) {
        // Pass remaining arguments (including vendor specific ones) to parent constructor
        super(message);

        // Maintains proper stack trace for where our error was thrown (only available on V8)
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, GracefulStopError)
        }
    }
}
