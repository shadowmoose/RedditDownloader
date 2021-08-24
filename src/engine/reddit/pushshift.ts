import axios from 'axios';
import DBComment from "../database/entities/db-comment";
import DBSubmission from "../database/entities/db-submission";

const PS_URL = 'https://api.pushshift.io/reddit/search/';

/** The more important bits of a PushShift Comment object, with some properties redacted for clarity. */
export interface PsComment {
    author: string;
    /** The 't2_' author ID. */
    author_fullname: string;
    /** The content of this message, in markdown. */
    body: string;
    created_utc: number;
    /** This comment's ID, 't1_'. */
    id: string;
    is_submitter: false;
    /** Parent Submission 't3_' ID */
    link_id: string;
    /** parent comment 't1_' ID. */
    parent_id: string;
    permalink: string;
    retrieved_on: number;
    score: number;
    /** Subreddit, without '/r/' prefix. */
    subreddit: string;
    /** The 't5_' subreddit ID. */
    subreddit_id: string;
}

/** The more important bits of a PushShift Submission object, with some properties redacted for clarity. */
export interface PsSubmission {
    author: string,
    /** The 't2_' author ID. */
    author_fullname: string,
    created_utc: number,
    /** The URL base of this submission's URL. */
    domain: string,
    /** The link to this Reddit thread. */
    full_link: string,
    /** The 't3_' id of this submission. */
    id: string,
    num_comments: number,
    over_18: boolean,
    permalink: string,
    retrieved_on: number,
    score: number,
    is_self: boolean;
    selftext: string,
    subreddit: string,
    link_flair_text: string;
    /** The 't5_' id of this submission's subreddit. */
    subreddit_id: string,
    title: string,
    upvote_ratio: number;
    /** The actual media URL submitted in this Submission. */
    url: string;
}

type PsTypeConversion<T> = T extends 'comment'
    ? PsComment
    : PsSubmission;
type PsDBConversion<T> = T extends 'comment'
    ? DBComment
    : DBSubmission;
type PsType = 'comment'|'submission';
export type PsPost = PsComment | PsSubmission;


export async function* scan<T extends PsType>(type: T, params: any, limit=0, oldestUTC = -1) {
    const url = `${PS_URL}${type}/`;
    let lastTime = Math.floor(Date.now()/1000);
    let ignore = new Set<string>();
    let found = 0;

    while (!oldestUTC || lastTime >= oldestUTC) {
        const res = await axios.get(url, {
            timeout: 15000,
            params: {
                ...params,
                before: lastTime,
                limit: Math.min(100, limit||100),
                sort: 'desc'
            }
        }).then(res => res.data);
        const posts: PsTypeConversion<T>[] = res.data.filter((p: PsPost) => {
            p.id = type === 'submission' ? `t3_${p.id}` : `t1_${p.id}`;
            return !ignore.has(p.id)
        });

        ignore.clear();
        if (posts.length) {
            lastTime = posts[posts.length-1].created_utc - 1;
        } else {
            return;
        }

        for (const p of posts) {
            if (p.created_utc < oldestUTC) return;
            ignore.add(p.id);
            yield await convertToDB(type, p);
            if (limit && ++found >= limit) {
                return;
            }
        }
    }
}


export function getUserComments(author: string, limit=0) {
    return scan('comment', {author}, limit);
}

export function getUserSubmissions(author: string, limit=0) {
    return scan('submission', {author}, limit);
}

export function getSubredditSubmissions(subreddit: string, limit=1000) {
    return scan('submission', {subreddit}, limit)
}

export async function getSubmission(...ids: string[]): Promise<DBSubmission|void> {
    const gen = await scan('submission', {ids: ids.join(',')}, 1);
    return (await gen.next()).value;
}

export async function getComment(...ids: string[]): Promise<DBComment|void> {
    const gen = await scan('comment', {ids: ids.join(',')}, 1);
    return (await gen.next()).value;
}


export async function convertToDB<T extends PsType>(type: T, data: PsPost): Promise<PsDBConversion<T>> {
    if (type === 'comment') {
        return await DBComment.fromPushShiftComment(data as PsComment) as any;
    } else {
        return DBSubmission.fromPushShiftSubmission(data as PsSubmission) as any;
    }
}
