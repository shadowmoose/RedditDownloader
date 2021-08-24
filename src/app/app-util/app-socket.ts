import {ClientCommand, ClientCommandTypes, ServerPacketTypes, SocketResponse} from "../../shared/socket-packets";
import {SettingsInterface, DownloaderStateInterface, RMDStatus} from "../../shared/state-interfaces";
import { observable } from "mobx"
import {SourceGroupInterface} from "../../shared/source-interfaces";

let ws: WebSocket|null = null;
let uid = 0;
let setConnected: any;
const awaitConnection = new Promise((res) => {
    setConnected = res;
});
const pendingCommands: Record<number, Function[]> = {};

/**
 * The current server-side state, synchronized with the web page via WebSocket.
 * Wrapped as a MobX Observable so that React components can efficiently listen for updates globally.
 */
export const STATE: DownloaderStateInterface = observable({
    activeDownloads: [],
    currentSource: null,
    currentState: RMDStatus.CLIENT_NOT_CONNECTED,
    finishedScanning: false,
    newPostsScanned: 1000,
    shouldStop: false
});

export const SETTINGS: SettingsInterface = {
    concurrentThreads: 0,
    createSymLinks: false,
    dedupeFiles: false,
    imgurClientId: "",
    minimumSimiliarity: 0,
    outputTemplate: "",
    refreshToken: "",
    serverHost: "",
    serverPort: 0,
    skipAlbumFiles: false,
    test: 0,
    userAgent: ""
};

export const SOURCE_GROUPS: SourceGroupInterface[] = observable([]);


/** Connect to the server's WebSocket, so that we can send or receive data. */
export function connectWS() {
    disconnectWS();
    ws = new WebSocket(location.origin.replace(/^http/, 'ws'));
    ws.onmessage = (event) => {
        const packet = JSON.parse(event.data);
        handleMessage(packet);
    };

    ws.onopen = setConnected;

    ws.onclose = () => {
        console.warn('Disconnected from RMD websocket!');
        for (const k of Object.keys(pendingCommands) as any) {
            failAck(k, 'Disconnected from RMD!');
        }
        ws = null;
    }
}

export function disconnectWS() {
    ws?.close();
    ws = null;
}

function sendRaw(data: string) {
    awaitConnection.then(() => {
        if (!ws) throw Error('No valid websocket connection - cannot send.');
        ws.send(data);
    })
}

export function sendCommand(type: ClientCommandTypes, data: any, timeout: number = 10000): Promise<any> {
    const packet: ClientCommand = {
        type,
        uid: ++uid,
        data
    }
    sendRaw(JSON.stringify(packet));

    return new Promise ((res, rej) => {
        let timer: any;
        if (timeout) {
            timer = setTimeout(() => {
                failAck(uid, `Command timed out! ${packet}`);
            }, timeout)
        }
        pendingCommands[uid] = [res, rej, ()=>clearTimeout(timer)];
    })
}

function handleMessage(packet: SocketResponse) {
    switch (packet.type) {
        case ServerPacketTypes.PING:
            return sendRaw('pong');

        case ServerPacketTypes.FULL_STATE:
            return clearState(packet.data);

        case ServerPacketTypes.STATE_CHANGE:
            return updateState(packet.data);

        case ServerPacketTypes.CURRENT_CONFIG:
            SOURCE_GROUPS.splice(0, SOURCE_GROUPS.length);
            SOURCE_GROUPS.push(...packet.data.sourceGroups);
            return Object.assign(SETTINGS, packet.data.settings);

        case ServerPacketTypes.ACK:
            return onAck(packet);

        default:
            console.error('Unknown packet:', packet);
    }
}

function updateState(data: any) {
    let cs: any = STATE;
    const path = data.path;
    const endKey = path.pop();

    path.forEach((p: any) => {
        if (!cs[p]) {
            if (data.deleted) return;
            cs[p] = {};
        }
        cs = cs[p];
    });

    if (data.deleted) {
        return delete cs[endKey];
    }
    cs[endKey] = data.value;
}

function clearState(newState?: any) {
    for (const key in STATE){
        if (STATE.hasOwnProperty(key)){
            // @ts-ignore
            delete STATE[key];
        }
    }

    if (newState) Object.assign(STATE, newState);
}

function onAck(packet: SocketResponse) {
    const idx = packet.uid || -1;
    const prom = pendingCommands[idx];

    console.log('Got ack', packet, pendingCommands);
    if (prom) {
        prom[2](); // Clear timer.
        delete pendingCommands[idx];
        if (packet.error) {
            failAck(idx, packet.error);
        } else {
            prom[0](packet.data);
        }
    }
}


function failAck(uid: number, error: string) {
    const prom = pendingCommands[uid];

    delete pendingCommands[uid];

    console.error('Failed ACK:', uid, error);

    if (prom) {
        prom[1](error);
    }
}


/**
 * Remove the given Source from the Group. Client-side modification only.
 * @param sourceGroupID
 * @param sourceID
 */
export function removeSource(sourceGroupID: number, sourceID: number) {
    const sg = SOURCE_GROUPS.find(sg => sg.id === sourceGroupID);
    if (!sg) throw Error('Invalid source group ID for Source deletion!');
    const idx = sg.sources.findIndex(s => s.id === sourceID);

    if (idx >= 0) {
        sg.sources.splice(idx);
        console.log('Deleted source from group:', sourceID, JSON.stringify(sg, null, 2));
    }
}


Object.assign(window, {
    debugState: () => JSON.parse(JSON.stringify(STATE)),
    debugSettings: () => SETTINGS,
    debugSourceGroups: () => JSON.parse(JSON.stringify(SOURCE_GROUPS)),
})
