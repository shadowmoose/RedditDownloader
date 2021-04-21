import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import { getManager } from 'typeorm';
import {SearchColumn} from "../../../shared/search-interfaces";


/**
 * Update/create a supported object type in the database.
 */
export class CommandListDownloads extends Command {
    type = ClientCommandTypes.LIST_DOWNLOADS;

    // TODO: Unit test this to be sure the queries don't break.
    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<any> {
        let {offset, limit, where} = pkt.data;
        limit = Math.min(limit, 200);

        const count = (await this.select(where, true))[0];
        const downloads = await this.select(where, false, limit, offset);

        return {
            downloads,
            count: count?.count
        }
    }

    private buildWhere(where: SearchColumn[]) {
        let strs: string[] = [];
        let vals = [];
        for (const w of where) {
            switch (w.column) {
                case 'title':
                    strs.push('submission.title like ?')
                    vals.push(w.value);
                    break;
                case 'author':
                    strs.push('(comment.id is not null and comment.author like ?) or submission.author like ?')
                    vals.push(w.value, w.value);
                    break;
                case 'body':
                    strs.push('submission.selfText like ? or comment.selfText like ?')
                    vals.push(w.value, w.value);
                    break;
                default:
                    throw Error(`The field "${w.column}" cannot be searched!`);
            }
        }
        return {
            where: strs.map(s => `(${s})`).join(' or '),
            vals
        };
    }

    private async select(whereOpts: SearchColumn[], count: boolean, limitNum = 0, offsetNum = 0) {
        const manager = getManager();
        const select = `
            file.path as path, 
            file.id as id, 
            submission.title as title,
            comment.author as commentAuthor,
            submission.author as submissionAuthor`;
        const {where, vals} = this.buildWhere(whereOpts);
        let filters = '';
        let filterVals: number[] = [];

        if (limitNum) {
            filters = filters + ' LIMIT ?';
            filterVals.push(limitNum);
        }
        if (offsetNum) {
            filters = filters + ' OFFSET ?';
            filterVals.push(offsetNum);
        }

        if (count) {
            filters = '';
            filterVals = [];
        }

        const sql = `
            select
                ${count? 'COUNT(*) as count' : select}
            from downloads dl
            left join comments comment on comment.id = dl.parentCommentId
            left join submissions submission
                on submission.id == dl.parentSubmissionId or submission.id = comment.rootSubmissionID
            left join urls url on url.id = dl.urlId
            left join files file on file.id = url.fileId
            where
                (dl.albumID is null or dl.isAlbumparent)
                and (url.processed and not url.failed)
                and (${where}) ${filters}`;
        const searchParams = [...vals, ...filterVals];

        // console.log(sql, searchParams);

        return manager.query(sql, searchParams);
    }
}
