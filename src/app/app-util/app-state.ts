import {ClientCommand, ServerPacketTypes, SocketResponse} from "../../shared/socket-packets";
import {SettingsInterface, DownloaderStateInterface, RMDStatus} from "../../shared/state-interfaces";
import { observable } from "mobx"

let ws: WebSocket|null = null;
let uid = 0;
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


/** Connect to the server's WebSocket, so that we can send or receive data. */
export function connectWS() {
    disconnectWS();
    ws = new WebSocket(location.origin.replace(/^http/, 'ws'));
    ws.onmessage = (event) => {
        const packet = JSON.parse(event.data);
        handleMessage(packet);
    };

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
    if (!ws) throw Error('No valid websocket connection - cannot send.')
    ws.send(data);
}

export function sendCommand(packet: ClientCommand, timeout: number = 10000): Promise<any> {
    packet.uid = uid++;
    sendRaw(JSON.stringify(packet));

    return new Promise ((res, rej) => {
        pendingCommands[uid] = [res, rej];
        if (timeout) {
            setTimeout(() => {
                failAck(uid, `Command timed out! ${packet}`);
            }, timeout)
        }
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
            return Object.assign(SETTINGS, packet.data);

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
    if (prom) {
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


Object.assign(window, {
    debugState: () => console.log(JSON.parse(JSON.stringify(STATE))),
    debugSettings: () => console.log(SETTINGS)
})
