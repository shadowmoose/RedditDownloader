
export enum RMDStatus {
    IDLE = 'idle',
    RUNNING = 'running',
    FINISHED = 'finished',
    /** Used by the client as the default value before an initial connection+sync has been made with the server. */
    CLIENT_NOT_CONNECTED = 'notConnected'
}

export interface DownloaderStateInterface {
    activeDownloads: (DownloaderProgressInterface|null)[];
    shouldStop: boolean;

    currentState: RMDStatus;
    finishedScanning: boolean;
    currentSource: string|null;

    newPostsScanned: number;
}


export interface DownloaderProgressInterface {
    thread: number;

    /**
     * User-friendly description of whatever is happening right now.
     */
    status: string;

    /**
     * The current (relative) file path that is being downloaded.
     */
    fileName: string;

    /**
     * The name of the current Handler trying to download.
     */
    downloader: string;

    /**
     * This indicates if the current download processor can currently know its total completion percentage.
     */
    knowsPercent: boolean;

    /**
     * Set internally as a signal to any supported running downloaders, that they should terminate.
     */
    shouldStop: boolean;

    /**
     * A float, representing the percentage complete this download is.
     */
    percent: number;
}


export type SettingsInterface = typeof defaultSettings;
export const defaultSettings = {
    test: 1337,
    refreshToken: '',
    userAgent: `RMD-${Math.random()}`,

    /** The maximum number of concurrent downloads. */
    concurrentThreads: 10,

    /** The output template RMD uses when generating a file name. */
    outputTemplate: '[subreddit]/[title] ([author])',

    /** If RMD should de-duplicate similar files after downloading. */
    dedupeFiles: true,
    /** If true, create symlinks to duplicate files in place of deleted, lower-quality files. */
    createSymLinks: true,
    /** The (hamming) distance that images should be. Any less, and they get deduplicated. */
    minimumSimiliarity: 3,
    /** If true, skip deduplication for all files that are within an album. */
    skipAlbumFiles: true,

    /** The host to launch the local webserver on. */
    serverHost: '127.0.0.1',
    /** The port to launch the local webserver on. */
    serverPort: 7001,

    /** The API to authenticate with imgur. */
    imgurClientId: ''
}
