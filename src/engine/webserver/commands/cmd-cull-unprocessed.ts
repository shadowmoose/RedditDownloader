import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import DBSubmission from "../../database/entities/db-submission";
import DBComment from "../../database/entities/db-comment";

/**
 * Delete all located Post that have not been downloaded, but are scheduled to be.
 */
export class CommandCullUnprocessed extends Command {
    type = ClientCommandTypes.CULL_UNPROCESSED;

    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        await DBSubmission.delete({shouldProcess: true, processed: false});  // Skip any parent-only submissions.
        await DBComment.delete({processed: false});
    }
}
