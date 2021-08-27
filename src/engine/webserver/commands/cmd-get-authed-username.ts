import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import {getRedditUsername} from "../../reddit/snoo";

/**
 * Return the username that is currently authorized to access Reddit, or null.
 */
export class CommandGetAuthedUsername extends Command {
    type = ClientCommandTypes.GET_AUTHED_USERNAME;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        return getRedditUsername();
    }
}
