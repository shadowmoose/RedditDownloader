import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import {getManager} from "typeorm";

/**
 * Save a setting's value.
 */
export class CommandGetAlbumFiles extends Command {
    type = ClientCommandTypes.GET_ALBUM_FILES;

    handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): any {
        const {albumID} = pkt.data;

        const manager = getManager();

        const sql = `
            SELECT
                f.id,
                f.mimeType
            FROM downloads dl
            LEFT JOIN urls u ON u.id = dl.urlId
            LEFT JOIN files f ON f.id = u.fileId
            WHERE
                u.processed = true
                AND dl.processed = true
                AND f.id is not null
                AND dl.albumID = ?
                AND dl.isAlbumParent = false
            ORDER BY albumPaddedIndex;
        `;

        return manager.query(sql, [albumID]);
    }
}
