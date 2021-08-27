import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import {getAccessToken} from "../../reddit/oAuth";
import DBSetting from "../../database/entities/db-setting";
import {disposeRedditAPI, getRedditUsername} from "../../reddit/snoo";

/**
 * Return a valid URL for Reddit oAuth.
 */
export class CommandSetOAuthCode extends Command {
    type = ClientCommandTypes.SET_OAUTH_CODE;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        const {code} = pkt.data;
        const token = await getAccessToken(code);

        await DBSetting.set('refreshToken', token||'');

        disposeRedditAPI();

        return getRedditUsername().catch(() => null);
    }
}
