import {DownloaderState, DownloaderStatus} from "./state";
import {SendFunction, Streamer} from "./streamer";
import {downloadAll} from "../downloaders/downloaders";
import DBSourceGroup from "../database/entities/db-source-group";
import {forGen} from "./generator-util";
import {isTest} from "./config";

let currentState: DownloaderState|null = null;


/**
 * Start scanning for new Posts, and also downloaing them.
 * Launches the process in a detatched Promise, and returns instantly so callers can reference the new state.
 * @param progressCallback
 */
export function scanAndDownload(progressCallback: SendFunction) {
    let state = getCurrentState();

    if (state.isRunning()) {
        throw Error('Unable to start a second scan before the first finishes.');
    }
    console.debug("Starting scan & download!")
    state.currentState = DownloaderStatus.RUNNING;

    const updater = new Streamer(state, progressCallback);

    return Promise
        .all([scanAll(state), downloadAll(state)])
        .catch(err => {
            console.error(err);
        }).finally(() => {
            state!.currentState = DownloaderStatus.FINISHED;
            state!.shouldStop = true;
            state!.currentSource = null;
            return updater;
        });
}

/**
 * Scan and save all Posts from all Source Groups.
 */
async function scanAll(state: DownloaderState) {
    const groups = await DBSourceGroup.find();  // TODO: Potentially allow 'specific source groups only'.

    for (const g of groups) {
        let found = await forGen(g.getPostGenerator(), async (ele, idx, stop) => {
            if (state.shouldStop) {
                return stop();
            }
            await ele.save();
            state.postsScanned ++;

            if (isTest() && state.postsScanned % 10 === 0) {
                console.debug(`Scanned ${state.postsScanned} posts so far...`)
            }
        });

        if (state.shouldStop) break;

        console.log(`Finished scanning group "${g.name}-${g.id}". Found ${found} new posts.`);
    }

    state.finishedScanning = true;
}

export function getCurrentState() {
    return currentState = currentState || new DownloaderState();
}
