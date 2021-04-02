import {Streamer} from "./streamer";
import {DownloadSubscriber} from "../database/entities/db-download";


export enum DownloaderStatus {
    IDLE = 'idle',
    RUNNING = 'running',
    FINISHED = 'finished'
}

export class DownloaderState {
    @Streamer.delay(500)
    activeDownloads: (DownloadProgress|null)[] = [];
    shouldStop = false;

    currentState: DownloaderStatus = DownloaderStatus.IDLE;
    finishedScanning = false;
    currentSource: string|null = null;

    @Streamer.delay(2000)
    newPostsScanned = 0;

    /**
     * Set the "shouldStop" flag on this state and all its relevant children.
     * Once set, all processing should respond and finish gracefully.
     *
     * This should only be called due to user intervention, in the case that they with to terminate an active run.
     */
    stop() {
        this.shouldStop = true;
        this.activeDownloads.forEach(a => {
            if (a) a.shouldStop = true
        });
        DownloadSubscriber.flush();
    }

    isRunning() {
        return this.currentState === DownloaderStatus.RUNNING
    }
}


export class DownloadProgress {
    constructor(thread: number) {
        this.thread = thread;
    }

    thread: number;

    /**
     * User-friendly description of whatever is happening right now.
     */
    @Streamer.delay(1000)
    status: string = '';

    @Streamer.delay(1000)
    fileName: string = '';

    /**
     * The name of the current Handler trying to download.
     */
    @Streamer.delay(1000)
    downloader: string = 'none';

    /**
     * This indicates if the current download processor can currently know its total completion percentage.
     */
    @Streamer.delay(500)
    knowsPercent: boolean = false;

    /**
     * Set internally as a signal to any supported running downloaders, that they should terminate.
     */
    shouldStop = false;

    /**
     * A float, representing the percentage complete this download is.
     */
    @Streamer.delay(1000)
    percent: number = 0;
}
