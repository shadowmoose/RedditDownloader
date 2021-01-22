import * as snoo from 'snoowrap';
import * as cheerio from 'cheerio';
import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";

function getHrefs(str: string|null): string[] {
    if (!str) return [];
    const $ = cheerio.load(str);

    // @ts-ignore
    return $('a')
        .toArray()
        .map(ele => $(ele).attr('href'))
        .filter(t => !!t);
}

const submissionExtractors: Record<string, (post: snoo.Submission)=>Promise<string[]>> = {
    'url': async (post: snoo.Submission) => {
        // @ts-ignore
        if (await post.is_gallery) return [];
        return [await post.url]
    },
    'bodyHTML': async (post: snoo.Submission) => {
        return getHrefs(await post.selftext_html);
    },
    'redditGallery': async (post: snoo.Submission) => {
        // @ts-ignore
        const meta: Record<any, any> = await post.media_metadata;
        // @ts-ignore
        const galleryData: any = await post.gallery_data;
        const ret: string[] = [];

        if (!meta || !galleryData.items) return [];

        const gKeys: string[] = galleryData.items.map((gd: any) => gd.media_id);

        for(const k of gKeys){
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

const commentExtractors: Record<string, (post: snoo.Comment)=>Promise<string[]>> = {
    'bodyHTML': async (post: snoo.Comment) => {
        return getHrefs(await post.body_html);
    }
};

export default async function extractLinks(post: DBSubmission | DBComment) {
    const extractors = post instanceof DBSubmission ? submissionExtractors : commentExtractors;
    const links: string[] = [];

    if (!post.loadedData) throw new Error('Unable to extract URLs from a non-loaded DB class!')

    for (const ex of Object.values(extractors)) {
        const res: string[] = await ex(post.loadedData);
        if (res) {
            res.forEach(r => {
                if (r && !links.includes(r)) links.push(r);
            })
        }
    }

    return links;
}
