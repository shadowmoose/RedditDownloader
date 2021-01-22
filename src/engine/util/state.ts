import {Streamer} from "./streamer";
import {DownloadSubscriber} from "../database/entities/db-download";


export class DownloaderState {
    activeDownloads: (DownloadProgress|null)[] = [];
    shouldStop = false;

    finishedScanning = false;
    currentSource: string|null = null;

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
}


export class DownloadProgress {
    /**
     * User-friendly description of whatever is happening right now.
     */
    status: string = '';

    /**
     * The name of the current Handler trying to download.
     */
    handler: string = 'none';

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
