import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";

/** Abstract representation of a handler class for client-provided commands. */
export default abstract class Command {
    public abstract type: ClientCommandTypes;
    public abstract handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): any;
}
