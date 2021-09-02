import {Streamer} from "../util/streamer";
import {DownloadSubscriber} from "../database/entities/db-download";
import {DownloaderProgressInterface, DownloaderStateInterface, RMDStatus} from "../../shared/state-interfaces";


export class DownloaderState implements DownloaderStateInterface {
    activeDownloads: (DownloadProgress|null)[] = [];
    shouldStop = false;

    currentState: RMDStatus = RMDStatus.IDLE;
    finishedScanning = false;
    currentSource: string|null = null;

    @Streamer.delay(2000)
    newPostsScanned = 0;
    downloadsInQueue = 0;

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



const percentTransformer = (newVal: number, prevVal: number): number => {
    const nv = Math.round((newVal * 100)) / 100;
    if (nv < 1 && Math.abs(nv - prevVal) < .1) {
        return prevVal;
    }
    return nv;
}


export class DownloadProgress implements DownloaderProgressInterface {
    constructor(thread: number) {
        this.thread = thread;
    }

    thread: number;

    status: string = 'Waiting for next available post.';

    fileName: string = '';

    downloader: string = '';

    knowsPercent: boolean = false;

    shouldStop = false;

    @Streamer.transformer(percentTransformer)
    percent: number = 0;

    url: string = '';
}

