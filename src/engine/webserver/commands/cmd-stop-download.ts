import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import * as dl from "../../core/download-controller";

/**
 * Signals to all running downloads that they should resolve ASAP, by toggling the "shouldStop" state value.
 */
export class CommandStopDownload extends Command {
    type = ClientCommandTypes.STOP_DOWNLOAD;

    handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): any {
        const state = dl.getCurrentState();
        if (state) {
            state.stop();
            return true;
        }
        return false;
    }
}
