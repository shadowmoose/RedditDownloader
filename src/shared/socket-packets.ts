/**
 * An incoming WS request, sent by the client to the server.
 */
export interface ClientCommand {
    uid: number;
    type: ClientCommandTypes;
    data?: any;
}

/**
 * A response object, send from the server to the client.
 */
export interface SocketResponse {
    uid?: number;
    type?: ServerPacketTypes;
    data?: any;
    error?: string;
}

export enum ClientCommandTypes {
    /** Request that a download be started. */
    START_DOWNLOAD = 'startDownload',
    /** Request that all downloading stop ASAP. */
    STOP_DOWNLOAD = 'stopDownload',
    /** Save a setting value. */
    SAVE_SETTING = 'saveSetting',
    /** Update a supported database object, using its ID. */
    UPDATE_OBJECT = 'updateObject',
    /** Delete a supported Database Object, using its ID. */
    DELETE_OBJECT = 'deleteObject',
    /** Delete all posts that have not yet been downloaded from previous runs. */
    CULL_UNPROCESSED = 'cullUnprocessed'
}

export enum ServerPacketTypes {
    /** The packet containing the current settings and source groups */
    CURRENT_CONFIG = 'currentConfig',
    /** Set a whole new state for the current download progress. */
    FULL_STATE = 'fullState',
    /** Signifies an incremental update to the current download state. */
    STATE_CHANGE = 'stateChange',
}
