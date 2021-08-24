import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import DBSourceGroup from "../../database/entities/db-source-group";
import DBSource from "../../database/entities/db-source";
import DBFilter from "../../database/entities/db-filter";
import DBSetting from "../../database/entities/db-setting";

/**
 * Delete a supported object type from the database.
 */
export class CommandDeleteDBObject extends Command {
    type = ClientCommandTypes.DELETE_OBJECT;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        const {id, dbType} = pkt.data;
        const dbClass = getClass(dbType);

        return dbClass.delete({ id });
    }
}


/**
 * Convert a string name into a real DB Entity class, if the given user-input name is valid & allowed.
 * Throws an error if the given type alias is invalid.
 */
export const getClass = (dbType: string) => {
    switch (dbType) {
        case 'DBSourceGroup':
            return DBSourceGroup;
        case 'DBSource':
            return DBSource;
        case 'DBFilter':
            return DBFilter;
        case 'DBSetting':
            return DBSetting;
        default:
            throw Error(`Unsupported db type alias: ${dbType}`);
    }
}
