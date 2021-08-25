import Command from "./command";
import {ClientCommand, ClientCommandTypes, ServerPacketTypes, SocketResponse} from "../../../shared/socket-packets";
import * as dl from "../../core/download-controller";
import {scanAndDownload} from "../../core/download-controller";

/**
 * Starts a new download if not already running, and attaches it to the broadcast functionality the webserver is using.
 */
export class CommandStartDownload extends Command {
    type = ClientCommandTypes.START_DOWNLOAD;

    handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): any {
        scanAndDownload((upd) => {
            broadcast({ type: ServerPacketTypes.STATE_CHANGE, data: upd })
        });
        broadcast({ type: ServerPacketTypes.FULL_STATE, data: dl.getCurrentState() });
    }
}
