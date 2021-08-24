import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import {getClass} from "./cmd-delete-dbobject";

/**
 * Update/create a supported object type in the database.
 * Only the properties that need to change must be included.
 */
export class CommandUpdateDBObject extends Command {
    type = ClientCommandTypes.UPDATE_OBJECT;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        const {id, dbType, newValues, parents} = pkt.data;
        const updClass = getClass(dbType);

        const existing = await updClass.findOne({id});
        // @ts-ignore
        const dbInstance = existing || updClass.build({...newValues});

        for (const k of Object.values(newValues)) {
            const val: any = dbInstance[k as keyof typeof dbInstance];

            if (typeof val === 'function' || val instanceof Promise) {
                throw Error(`Cannot overwrite property: ${k}`);
            }
        }

        Object.assign(dbInstance, newValues);

        if (parents) {
            await injectParents(dbInstance, parents);
        }

        await dbInstance.save();

        return {status: existing ? 'Updated' : 'Created', id: dbInstance.id };
    }
}


async function injectParents(instance: any, parents: any) {
    for (const p of parents) {
        const {dbType, id, property} = p;
        const clazz = getClass(dbType);
        const parentInstance = await clazz.findOne({ id });

        if (!parentInstance) throw Error(`Could not locate parent instance: ${p}`);

        instance[property] = parentInstance;
    }
}
