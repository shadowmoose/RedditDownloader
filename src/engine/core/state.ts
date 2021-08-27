import {Streamer} from "../util/streamer";
import {DownloadSubscriber} from "../database/entities/db-download";
import {DownloaderProgressInterface, DownloaderStateInterface, RMDStatus} from "../../shared/state-interfaces";


export class DownloaderState implements DownloaderStateInterface {
    @Streamer.delay(500)
    activeDownloads: (DownloadProgress|null)[] = [];
    shouldStop = false;

    currentState: RMDStatus = RMDStatus.IDLE;
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
        DownloadSubscriber.toggle(false);
    }

    isRunning() {
        return this.currentState === RMDStatus.RUNNING
    }
}


export class DownloadProgress implements DownloaderProgressInterface {
    constructor(thread: number) {
        this.thread = thread;
    }

    thread: number;

    @Streamer.delay(1000)
    status: string = '';

    @Streamer.delay(1000)
    fileName: string = '';

    @Streamer.delay(1000)
    downloader: string = 'none';

    @Streamer.delay(500)
    knowsPercent: boolean = false;

    shouldStop = false;

    @Streamer.delay(1000)
    @Streamer.transformer(number => (Math.round(number * 100) / 100))
    percent: number = 0;
}
