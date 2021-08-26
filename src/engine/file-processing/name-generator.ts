import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";
import DBDownload from "../database/entities/db-download";
import {getAbsoluteDL} from "../core/paths";
import DBFile from "../database/entities/db-file";
import {forkPost} from "../database/db";
import {mutex} from "../util/promise-pool";
import {TemplateTags} from "../../shared/name-template";

const sanitize = require('sanitize-filename');

export const MAX_NAME_LEN = 240;


export const makeName = mutex(async (dl: DBDownload, template: string, usedFileNames: string[] = []) => {
    const parent = await dl.getDBParent();
    const tags = await forkPost(parent,
            c => getCommentValues(c),
            s => getSubmissionValues(s));

    const countMatches = async() => {
        return DBFile
            .createQueryBuilder('f')
            .select()
            .where('f.path LIKE :path', {path: `${path}%`})
            .getCount();
    };

    const alParent = (dl.albumID && !dl.isAlbumParent) ? await DBDownload.findOne({isAlbumParent: true, albumID: dl.albumID}): null;
    const parentDir = (await (await alParent?.url)?.file)?.path;
    let base = parentDir ? parentDir+dl.albumPaddedIndex : makePathFit(tags, template).replace(/^[./\\]/, '');
    let path = base;
    let idx = 1;

    while (await countMatches() || usedFileNames.find(p => p===path)) {
        path = base + ` - ${++idx}`;
    }

    return path;
});

/**
 * Generates a file subpath which, when in absolute form, fits within the filename limit for the OS.
 * @param tags
 * @param template
 */
export function makePathFit(tags: TemplateTags, template: string) {
    let res = '';
    let len = MAX_NAME_LEN - 5;  // leave space for Jesus.
    do {
        res = insert(tags, template, len);
    } while (getAbsoluteDL(res).length > MAX_NAME_LEN && --len)
    if (!len) throw Error(`Unable to generate a short enough file path to save download! ${tags}`);

    return res;
}

export async function getCommentValues(c: DBComment): Promise<TemplateTags> {
    const root = await c.parentSubmission;

    return {
        author: c.author,
        createdDate: yyyymmss(c.createdUTC),
        id: c.id,
        over18: root?.over18||true,
        score: c.score,
        subreddit: c.subreddit,
        title: root?.title||'[unknown title]',
        type: 'comment'
    }
}

export async function getSubmissionValues(s: DBSubmission): Promise<TemplateTags> {
    return {
        author: s.author,
        createdDate: yyyymmss(s.createdUTC),
        id: s.id,
        over18: s.over18,
        score: s.score,
        subreddit: s.subreddit,
        title: s.title,
        type: 'submission'
    }
}

/**
 * Insert the given tag object map into the given string template.
 */
export function insert(tags: TemplateTags, template: string, len: number = 255) {
    const open = `${Math.random()}`;
    const close = `${Math.random()}`;
    let out = template;
    for (const [k,v] of Object.entries(tags)) {
        const shortened = clean(`${v}`).substring(0, len);
        const value = replaceAll(replaceAll(shortened, '\\[', open), '\\]', close);
        out = replaceAll(out, `\\[${k}\\]`, value);
    }

    return replaceAll(replaceAll(out, open, '['), close, ']');
}

function replaceAll(str: any, search: string, newVal: string): string {
    return `${str}`.replace(new RegExp(search, 'gmi'), newVal);
}

function clean(str: string): string {
    return sanitize(str, {
        replacement: '_'
    });
}


function yyyymmss(utc: number) {
    const date = new Date(utc*1000);
    const padded = (val: any, len=2) => `${val}`.padStart(len, '0');
    return padded(date.getFullYear(), 4) + "-" + padded(date.getMonth()+1) + "-" + padded(date.getDate())
}
