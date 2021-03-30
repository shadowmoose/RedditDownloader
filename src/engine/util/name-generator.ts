import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";
import DBDownload from "../database/entities/db-download";
import {getAbsoluteDL} from "./paths";
import DBFile from "../database/entities/db-file";
import {forkPost} from "../database/db";
import {mutex} from "./promise-pool";
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
    type: 'comment'|'submission';
}


export const makeName = mutex(async (dl: DBDownload, template: string, usedFileNames: string[] = []) => {
    const parent = await dl.getDBParent();
    const tags = await forkPost(parent,
            c => getCommentValues(c),
            s => getSubmissionValues(s));
    tags.url = (await dl.url).address;

    const countMatches = async() => {
        return DBFile
            .createQueryBuilder('f')
            .select()
            .where('f.path LIKE :path', {path: `${path}%`})
            .getCount();
    };

    const alParent = (dl.albumID && !dl.isAlbumParent) ? await DBDownload.findOne({where: {isAlbumParent: true, albumID: dl.albumID}, relations: ['url']}): null;
    const parentDir = (await (await alParent?.url)?.file)?.path;
    let base = parentDir ? parentDir+dl.albumPaddedIndex : makePathFit(tags, template, dl.albumPaddedIndex).replace(/^[./\\]/, '');
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
 * @param albumIDX If non-null, the template is used as a subdirectory, and the file name within is this index.
 */
export function makePathFit(tags: TemplateTags, template: string, albumIDX: string|null = null) {
    let res = '';
    let len = 245;
    if (albumIDX) {
        template = template + '/' + albumIDX; // TODO: Test this to be sure it always works.
    }
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
