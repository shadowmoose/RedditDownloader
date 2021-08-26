import express from 'express';
import ws from 'ws';
import DBSetting from "../database/entities/db-setting";
import {ClientCommand, ServerPacketTypes, SocketResponse} from "../../shared/socket-packets";
import * as dl from '../core/download-controller';
import Command from "./commands/command";
import {CommandStartDownload} from "./commands/cmd-start-download";
import {CommandStopDownload} from "./commands/cmd-stop-download";
import {CommandDeleteDBObject} from "./commands/cmd-delete-dbobject";
import DBSourceGroup from "../database/entities/db-source-group";
import {CommandCullUnprocessed} from "./commands/cmd-cull-unprocessed";
import {makeDB} from "../database/db";
import {CommandUpdateDBObject} from "./commands/cmd-update-dbobject";
import {CommandSaveSetting} from "./commands/cmd-save-setting";
import DBFile from "../database/entities/db-file";
import {getAbsoluteDL} from "../core/paths";
import path from "path";
import {Server} from "http";
import {CommandListDownloads} from "./commands/cmd-list-downloads";


/** All available command processors. */
const commands: Command[] = [
    new CommandStartDownload(),
    new CommandStopDownload(),
    new CommandDeleteDBObject(),
    new CommandUpdateDBObject(),
    new CommandCullUnprocessed(),
    new CommandSaveSetting(),
    new CommandListDownloads()
];
export const clients: ws[] = [];
export const app = express();
const wsServer = new ws.Server({ noServer: true });

/* Serve an index file. */
app.use(express.static(path.resolve(path.dirname(__filename), '../../../dist/')));

console.log('Serving static files from:', path.resolve(path.dirname(__filename), '../../../dist/'));

/* Serve downloaded files, using their ID. */
app.get('/file/:id', async (req, res) => {
    const f = await DBFile.findOne({id: parseInt(req.params.id)});
    if (!f) {
        return res.status(404).send('Unknown file ID.');
    }

    if (!req.headers.range) console.log('Serving file:', req.params.id, '->', path.basename(f.path));

    return res.sendFile(getAbsoluteDL(f.path), {
        headers: {
            'Content-Disposition': 'inline; filename=' + encodeURIComponent(path.basename(f.path))
        }
    });
});


wsServer.on('connection', async socket => {
    console.debug('Client connected via WebSocket.');

    resetPing(socket, true);

    socket.on("error", () => socket.close(500, 'Encountered critical internal error.'));
    socket.on('close', () => {
        removeClient(socket);
        resetPing(socket);
    });
    socket.on('message', async message => {
        resetPing(socket, true);
        if (message === 'pong') {
            // Handle pings "out of band" since they may be required before any validation handlers.
            return;
        }

        console.log('[server] Incoming message:', message);

        try {
            await handleMessage(socket, JSON.parse(`${message}`));
        } catch (err) {
            // Packet is malformed.
            console.error(err);
            socket.close(4000, 'Malformed packet.');
        }
    });

    const groups = await DBSourceGroup.find();

    // Send some of the initial data that the client will always want:
    send(socket, {
        type: ServerPacketTypes.CURRENT_CONFIG,  // Send config first to avoid any possible client-side race conditions.
        data: {
            settings: await DBSetting.getAll(),
            sourceGroups: await Promise.all(groups.map(g => g.toSimpleObject()))
        }
    });
    send(socket, { type: ServerPacketTypes.FULL_STATE, data: dl.getCurrentState() });

    clients.push(socket);
});


/**
 * Clears any currently scheduled disconnect timer from the client, and optionally schedules a new one.
 * @param client
 * @param reCheck
 */
function resetPing(client: any, reCheck: boolean = false) {
    clearTimeout(client.pingCheck);
    client.pingCheck = reCheck ? setTimeout(() => {
        client.pingCheck = setTimeout(() => {
            console.error('Missing Ping: Websocket Client timed out.');
            client.close(4001, 'Client timed out.');
        }, 10000)
        send(client, {type: ServerPacketTypes.PING, data: Date.now()});
    }, 25000) : null;
}


/**
 * Start the local HTTP & WebSockeet server.
 */
export async function launchServer(): Promise<Server> {
    console.log("Launching server...");
    return new Promise(async (res) => {
        const host = await DBSetting.get('serverHost');
        const port = await DBSetting.get('serverPort');
        const server = app.listen(port, host, () => {
            console.debug(`[ENTRYPOINT] Server listening on http://${host}:${port}`);
            res(server);
        });

        server.on('upgrade', (request, socket, head) => {
            wsServer.handleUpgrade(request, socket, head, socket => {
                wsServer.emit('connection', socket, request);
            });
        });
    })
}


/**
 * Process incoming messages from connected clients.
 */
async function handleMessage(sock: ws, pkt: ClientCommand) {
    try {
        for (const c of commands) {
            if (c.type === pkt.type) {
                const resp = await c.handle(pkt, broadcast);

                if (pkt.uid !== null && pkt.uid !== undefined) {
                    return send(sock, {
                        type: ServerPacketTypes.ACK,
                        uid: pkt.uid,
                        data: resp
                    })
                }
            }
        }
    } catch (err) {
        console.error(err);
        send(sock,{error: err.message, uid: pkt.uid});
        return;
    }
    throw Error(`Unable to handle the given unknown command type: ${pkt.type}`);
}

/**
 * Remove the given client socket from the tracked connected list.
 */
export function removeClient(sock: ws) {
    const idx = clients.indexOf(sock);
    if (idx > -1) {
        clients.splice(idx, 1);
        console.debug('Client disconnected from WebSocket.');
    }
}

/**
 * Send a message to a connected client socket.
 */
export function send(sock: ws, message: SocketResponse) {
    try {
        sock.send(JSON.stringify(message), err => {
            if (err) {
                console.error(err);
                sock.close();
            }
        });
    } catch (err) {
        console.error('Failed to send to ws client.')
        sock.close();
    }
}

/**
 * Send a message to all connected clients.
 */
export function broadcast(message: SocketResponse) {
    clients.forEach(c => send(c, message))
}


export async function startServer() {
    console.debug("Starting up...");
    await makeDB();
    console.debug('Made DB.');
    return launchServer();
}

if (require.main === module) {
    startServer()
}
