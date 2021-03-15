import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import DBSetting from "../../database/entities/db-setting";

/**
 * Save a setting's value.
 */
export class CommandSaveSetting extends Command {
    type = ClientCommandTypes.SAVE_SETTING;

    handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): any {
        const {key, value} = pkt.data;

        return DBSetting.set(key, value);
    }
}
