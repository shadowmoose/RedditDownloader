import express from 'express';
import ws from 'ws';
import DBSetting from "../database/entities/db-setting";
import {ClientCommand, ServerPacketTypes, SocketResponse} from "../../shared/socket-packets";
import * as dl from '../util/download-controller';
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
import {getAbsoluteDL} from "../util/paths";
import path from "path";


/** All available command processors. */
const commands: Command[] = [
    new CommandStartDownload(),
    new CommandStopDownload(),
    new CommandDeleteDBObject(),
    new CommandUpdateDBObject(),
    new CommandCullUnprocessed(),
    new CommandSaveSetting()
];
export const clients: ws[] = [];
export const app = express();
const wsServer = new ws.Server({ noServer: true });

/* Serve an index file. */
app.get('/', function(req, res){
    res.sendFile(path.resolve(path.dirname(__filename), './test-socket.html'));  // TODO: Replace with a real index.
});

/* Serve downloaded files, using their ID. */
app.get('/file/:id', async (req, res) => {
    const f = await DBFile.findOne({id: parseInt(req.params.id)});
    if (!f) {
        return res.status(404).send('Unknown file ID.');
    }

    console.log('Serving file:', req.params.id, '->', path.basename(f.path));
    return res.sendFile(getAbsoluteDL(f.path), {
        headers: {
            'Content-Disposition': 'inline; filename=' + encodeURIComponent(path.basename(f.path))
        }
    });
});


wsServer.on('connection', async socket => {
    console.debug('Client connected via WebSocket.');

    socket.on("error", () => socket.close(500, 'Encountered critical internal error.'));
    socket.on('close', () => {
        removeClient(socket)
    });
    socket.on('message', async message => {
        console.log('Incoming message:', message);
        try {
            await handleMessage(socket, JSON.parse(`${message}`));
        } catch (err) {
            // Packet is malformed.
            console.error(err);
            socket.close(400, 'Malformed packet.');
        }
    });

    const groups = await DBSourceGroup.find();

    // Send some of the initial data that the client will always want:
    send(socket, {
        type: ServerPacketTypes.CURRENT_CONFIG,
        data: {
            settings: await DBSetting.getAll(),
            sourceGroups: await Promise.all(groups.map(g => g.toSimpleObject()))
        }
    });
    send(socket, { type: ServerPacketTypes.FULL_STATE, data: dl.getCurrentState() });

    clients.push(socket);
});


// TODO: Add an express route for locally-built website, for when not running through Electron.


/**
 * Start the local HTTP & WebSockeet server.
 */
export async function launchServer() {
    console.log("Launching server...");
    const host = await DBSetting.get('serverHost');
    const port = await DBSetting.get('serverPort');
    const server = app.listen(port, host, () => {
        console.debug(`Server listening on http://${host}:${port}`);
    });

    server.on('upgrade', (request, socket, head) => {
        wsServer.handleUpgrade(request, socket, head, socket => {
            wsServer.emit('connection', socket, request);
        });
    });

    return server;
}


/**
 * Process incoming messages from connected clients.
 */
async function handleMessage(sock: ws, pkt: ClientCommand) {
    try {
        for (const c of commands) {
            if (c.type === pkt.type) {
                const resp = await c.handle(pkt, broadcast);

                return send(sock, {
                    uid: pkt.uid,
                    data: resp
                })
            }
        }
        throw Error(`Unable to handle the given unknown command type: ${pkt.type}`);
    } catch (err) {
        console.error(err);
        send(sock,{error: err.message, uid: pkt.uid});
    }
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
        console.error('Failed to send to client.')
        sock.close();
    }

}

/**
 * Send a message to all connected clients.
 */
export function broadcast(message: SocketResponse) {
    clients.forEach(c => send(c, message))
}


if (require.main === module) {
    new Promise( async () => {
        console.debug("Starting up...");
        await makeDB();
        console.debug('Made DB.');
        await launchServer();
    }).catch(err => {
        console.error(err)
    })
}