import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import DBSourceGroup from "../../database/entities/db-source-group";

/**
 * Update or create a DBSourceGroup.
 */
export class CommandUpdateSourceGroup extends Command {
    type = ClientCommandTypes.UPDATE_GROUP;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        const data = pkt.data;
        const existing = await DBSourceGroup.findOne({id: pkt.data.id});
        const grp = existing || DBSourceGroup.build({...pkt.data});

        for (const k of Object.values(data)) {  // TODO: Better safety check, possibly using JSON schema.
            const val = grp[k as keyof typeof grp];
            if (!grp.hasOwnProperty(`${k}`)) throw Error(`Invalid property: ${k}`);
            if (typeof val === 'function' || val instanceof Promise) {
                throw Error(`Cannot overwrite property: ${k}`);
            }
        }

        Object.assign(grp, data);

        await grp.save();

        return true;
    }
}
