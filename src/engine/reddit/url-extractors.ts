import * as snoo from 'snoowrap';
import * as cheerio from 'cheerio';
import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";
import {PsComment, PsSubmission} from "./pushshift";
import getUrls from 'get-urls';


function getHrefs(str: string|null): string[] {
    if (!str) return [];
    const $ = cheerio.load(str);

    // @ts-ignore
    return $('a')
        .toArray()
        .map(ele => $(ele).attr('href'))
        .filter(t => !!t);
}

const submissionExtractors: Record<string, (post: snoo.Submission, pushshift: boolean)=>Promise<string[]>> = {
    'url': async (post: snoo.Submission | PsSubmission, _ps: boolean) => {
        // @ts-ignore
        if (await post.is_gallery) return [];
        return [await post.url]
    },
    'bodyHTML': async (post: snoo.Submission | PsSubmission, ps: boolean) => {
        if (ps) return Array.from(getUrls(post.selftext));
        // @ts-ignore
        return getHrefs(await post.selftext_html);
    },
    'redditGallery': async (post: snoo.Submission | PsSubmission, _ps: boolean) => {
        // @ts-ignore
        const meta: Record<any, any> = await post.media_metadata;
        // @ts-ignore
        const galleryData: any = await post.gallery_data;
        const ret: string[] = [];

        if (!meta || !galleryData.items) return [];

        const gKeys: string[] = galleryData.items.map((gd: any) => gd.media_id);

        for (const k of gKeys) {
            const m = meta[k];
            Object.values(m).forEach((s: any) => {
                if (!s.x || !s.y) return;
                const url: any = Object.values(s).find(v => `${v}`.startsWith('http'));
                if (url) ret.push(url);
            });
        }
        return ret;
    }
};

const commentExtractors: Record<string, (post: snoo.Comment, isPs: boolean)=>Promise<string[]>> = {
    'bodyHTML': async (post: snoo.Comment | PsComment, ps: boolean) => {
        if (ps) return Array.from(getUrls(post.body))
        // @ts-ignore
        return getHrefs(await post.body_html);
    },
};


/**
 * Extract the URLs from the given Post, checking both direct links and body text.
 * @param post
 */
export default async function extractLinks(post: DBSubmission | DBComment) {
    const extractors = post instanceof DBSubmission ? submissionExtractors : commentExtractors;
    const links: string[] = [];

    if (!post.loadedData) throw new Error('Unable to extract URLs from a non-loaded DB class!')

    for (const ex of Object.values(extractors)) {
        const res: string[] = await ex(post.loadedData, post.fromPushshift);
        if (res) {
            res.forEach(r => {
                if (r && !links.includes(r) && !r.startsWith('/r/')) links.push(r);
            })
        }
    }

    return links;
}
