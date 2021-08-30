import {broadcast} from "../webserver/web-server";
import {ServerPacketTypes} from "../../shared/socket-packets";

export const socketnotifications = {
    error: (msg: string) => broadcast({
        type: ServerPacketTypes.GLOBAL_ERROR,
        data: msg
    })
};
export type Notifier = typeof socketnotifications;


let notifier: Notifier = socketnotifications;

/**
 * Change the wrapper that is used to send notifications from RMD's core during runtime.
 * @param newNotifier
 */
export function setNotifier(newNotifier: Notifier) {
    notifier = newNotifier;
}


/**
 * Send an error to all clients, using the registered Notifier.
 * @param message
 */
export function sendError(message: string|Error) {
    let msg = `${message}`;
    if (message instanceof Error) {
        msg = message.message;
    }

    notifier.error(msg);
}
