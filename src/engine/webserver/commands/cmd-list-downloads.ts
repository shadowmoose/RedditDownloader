import Command from "./command";
import {ClientCommand, ClientCommandTypes, SocketResponse} from "../../../shared/socket-packets";
import { getManager } from 'typeorm';
import {
    DownloadSearchResponse, SearchableField,
    SearchColumn,
    SearchCommand,
    DownloadSearchResult
} from "../../../shared/search-interfaces";


/**
 * Update/create a supported object type in the database.
 */
export class CommandListDownloads extends Command {
    type = ClientCommandTypes.LIST_DOWNLOADS;

    // TODO: Unit test this to be sure the queries don't break.
    async handle(pkt: ClientCommand, broadcast: (message: SocketResponse)=>void): Promise<DownloadSearchResponse> {
        let search: SearchCommand = pkt.data;
        search.limit = Math.min(search.limit, 200);

        const count = (await this.select(search, true))[0];
        const downloads: DownloadSearchResult[] = await this.select(search, false);

        await Promise.all(downloads.filter((d)=>d.isAlbumParent).map(async (d) => {
            console.debug('lookup album details:', d.albumID);

            d.albumFiles = await this.selectAlbumInfo(d.albumID!);  // TODO: Type this.
        }));

        console.debug('[server] responding to search.');
        return {
            downloads,
            count: count?.count || 0
        }
    }

    private buildWhere(where: SearchColumn[], matchAll: boolean) {
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
                case 'subreddit':
                    const vl = w.value.replace('r/', '').replace('/', '');
                    strs.push('(comment.id is not null and comment.subreddit like ?) or submission.subreddit like ?')
                    vals.push(vl, vl);
                    break;
                default:
                    throw Error(`The field "${w.column}" cannot be searched!`);
            }
        }

        return {
            whereStrings: strs.map(s => `(${s})`).join(matchAll ? ' and ' : ' or ').trim() || '1=1',
            vals
        };
    }

    private translateOrderBy(field: SearchableField) {
        switch (field) {
            case 'author':
                return 'COALESCE(comment.author, submission.author)'
            case 'body':
                return 'COALESCE(comment.selfText, submission.selfText)'
            case 'subreddit':
                return 'COALESCE(comment.subreddit, submission.subreddit)'
            default:
                return field
        }
    }

    private async select(search: SearchCommand, countOnly: boolean) {
        const {where, limit, offset, order, ascending, matchAll} = search;
        const manager = getManager();
        const select = `
            file.path as path, 
            file.id as id, 
            file.mimeType as type,
            dl.isAlbumParent as isAlbumParent,
            dl.albumId,
            dl.id as dlUID,
            submission.title as title,
            COALESCE(comment.author, submission.author) as author,
            CASE WHEN comment.id is null THEN 'submission' ELSE 'comment' END AS postType,
            COALESCE(comment.selfText, submission.selfText) as postText,
            COALESCE(comment.id, submission.id) as postId`;
        const {whereStrings, vals} = this.buildWhere(where, !!matchAll);
        let filters = '';
        let filterVals: number[] = [];
        let orderBy = '';

        if (limit) {
            filters = filters + ' LIMIT ?';
            filterVals.push(limit);
        }
        if (offset) {
            filters = filters + ' OFFSET ?';
            filterVals.push(offset);
        }
        if (order) {
            orderBy = `ORDER BY ${this.translateOrderBy(order)} ${ascending ? 'ASC' : 'DESC'}`;
        }

        if (countOnly) {
            filters = '';
            filterVals = [];
        }

        const sql = `
            select
                ${countOnly? 'COUNT(*) as count' : select}
            from downloads dl
            left join comments comment on comment.id = dl.parentCommentId
            left join submissions submission
                on submission.id == dl.parentSubmissionId or submission.id = comment.parentSubmissionId
            left join urls url on url.id = dl.urlId
            left join files file on file.id = url.fileId
            where
                (dl.albumID is null or dl.isAlbumparent)
                and (url.processed and not url.failed)
                and (${whereStrings}) ${orderBy} ${filters}`;
        const searchParams = [...vals, ...filterVals];

        // console.log(sql, searchParams);

        return manager.query(sql, searchParams);
    }

    private async selectAlbumInfo(id: string) {
        const manager = getManager();
        const firstFile = await manager.query(`
            select
                file.id as id,
                file.mimeType as type
            from downloads dl
                left join urls u on u.id = dl.urlId
                left join files file on file.id = u.fileId
            where dl.albumId = ? and not dl.isAlbumparent and u.processed and not u.failed
            order by dl.albumPaddedIndex asc limit 1
        `, [id]);

        const total = await manager.query(`
            select COUNT(*) as total
            from downloads dl
                left join urls u on u.id = dl.urlId
                left join files file on file.id = u.fileId
            where 
              dl.albumId = ?
              and not dl.isAlbumparent
        `, [id]);

        return {
            firstFile: firstFile[0],
            count: total[0].total
        }
    }
}
