/**
 * A WS-based request, sent by the client (browser) to the server.
 */
export interface ClientCommand {
    uid?: number;
    type: ClientCommandTypes;
    data?: any;
}

/**
 * A response object, send from the server to the client (browser).
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
    CULL_UNPROCESSED = 'cullUnprocessed',
    /** Return a paginated section of the available downloads matching the given query. */
    LIST_DOWNLOADS = 'listDownloads',
    /** Return a valid Reddit URL for authentication flow. */
    GET_OAUTH_URL = 'getOAuth',
    /** Set the oAuth code for RMD to use in retrieving a refresh token. */
    SET_OAUTH_CODE = 'setOAuth',
    /** Set the oAuth code for RMD to use in retrieving a refresh token. */
    GET_AUTHED_USERNAME = 'getUsername',
    /** Get a full list of files for the given album code. */
    GET_ALBUM_FILES = 'getAlbumFiles',
}

export enum ServerPacketTypes {
    /** The packet containing the current settings and source groups */
    CURRENT_CONFIG = 'currentConfig',
    /** Set a whole new state for the current download progress. */
    FULL_STATE = 'fullState',
    /** Signifies an incremental update to the current download state. */
    STATE_CHANGE = 'sc',
    /** The server is requesting a "pong" response, in a timely manner. */
    PING = 'ping',
    /** A response from the server, for a specific client command. */
    ACK = 'ack',
    /** An error that all clients should be aware of, and display. */
    GLOBAL_ERROR = 'globalError'
}
