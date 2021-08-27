import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import {authorizationURL} from "../../reddit/oAuth";

/**
 * Return a valid URL for Reddit oAuth.
 */
export class CommandGetOAuthUrl extends Command {
    type = ClientCommandTypes.GET_OAUTH_URL;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        return authorizationURL()
    }
}
