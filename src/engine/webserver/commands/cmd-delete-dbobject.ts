import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import DBSourceGroup from "../../database/entities/db-source-group";
import DBSource from "../../database/entities/db-source";
import DBFilter from "../../database/entities/db-filter";

/**
 * Delete a supported object type from the database.
 */
export class CommandDeleteDBObject extends Command {
    type = ClientCommandTypes.DELETE_OBJECT;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        const {id, delType} = pkt.data.dbType;
        let dbType = null;

        switch (delType) {
            case 'DBSourceGroup':
                dbType = DBSourceGroup;
                break;
            case 'DBSource':
                dbType = DBSource;
                break;
            case 'DBFilter':
                dbType = DBFilter;
                break;
            default:
                throw Error(`Unsupported type for deletion: ${delType}`);
        }

        if (dbType) {
            return dbType.delete({ id });
        }
    }
}
