import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";
import DBDownload from "../database/entities/db-download";
import {getAbsoluteDL} from "./paths";
import DBFile from "../database/entities/db-file";
import {forkPost} from "../database/db";
const sanitize = require('sanitize-filename');

export const MAX_NAME_LEN = 240;

export interface TemplateTags {
    id: string;
    title: string;
    author: string;
    subreddit: string;
    score: number;
    createdUTC: number;
    over18: boolean;

    url: string;
    type: 'comment'|'submission'
}

export async function makeName(dl: DBDownload, template: string) {
    const parent = await dl.getDBParent();
    const tags = await forkPost(parent,
            c => getCommentValues(c),
            s => getSubmissionValues(s));
    tags.url = dl.url.address;

    const countMatches = async() => {
        return DBFile
            .createQueryBuilder('f')
            .select()
            .where('f.path LIKE :path', {path: `${path}%`})
            .getCount();
    };
    const baseName = makePathFit(tags, template).replace(/^[./\\]/, '');
    let path = baseName;
    let idx = 1;

    while (await countMatches()) {
        path = `${baseName} - ${++idx}`
    }

    return path;
}

export function makePathFit(tags: TemplateTags, template: string) {
    let res = '';
    let len = 255;
    do {
        res = insert(tags, template, len);
    } while (getAbsoluteDL(res).length > MAX_NAME_LEN && --len)
    if (!len) throw Error(`Unable to generate a short enough file path to save download! ${tags}`);

    return res;
}

export async function getCommentValues(c: DBComment): Promise<TemplateTags> {
    const root = await c.getRootSubmission();

    return {
        author: c.author,
        createdUTC: c.createdUTC,
        id: c.id,
        over18: root?.over18||true,
        score: c.score,
        subreddit: c.subreddit,
        title: root?.title||'[unknown title]',
        url: "",
        type: 'comment'
    }
}

export async function getSubmissionValues(s: DBSubmission): Promise<TemplateTags> {
    return {
        author: s.author,
        createdUTC: s.createdUTC,
        id: s.id,
        over18: s.over18,
        score: s.score,
        subreddit: s.subreddit,
        title: s.title,
        url: "",
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
