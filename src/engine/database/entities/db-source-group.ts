import {Entity, Column, PrimaryGeneratedColumn, OneToMany} from 'typeorm';
import {DBEntity} from "./db-entity";
import DBComment from "./db-comment";
import DBFilter from "./db-filter";
import DBSource from "./db-source";
import {makeSource} from "../../sources";
import DBSubmission from "./db-submission";
import {filterMap} from "../../util/generator-util";
import {DBPost, forkPost} from "../db";
import extractLinks from "../../reddit/url-extractors";
import DBDownload from "./db-download";
import {SourceGroupInterface} from "../../../shared/source-interfaces";
import {DownloaderState} from "../../core/state";
import {sendError} from "../../core/notifications";


@Entity({ name: 'source_groups' })
export default class DBSourceGroup extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column({ length: 36 })
    name!: string;

    @Column({ length: 36, nullable: false })
    color!: string;

    @OneToMany(() => DBFilter, f => f.sourceGroup, {cascade: true})
    filters!: Promise<DBFilter[]>;

    @OneToMany(() => DBSource, f => f.sourceGroup, {cascade: true})
    sources!: Promise<DBSource[]>;

    /**
     * Generate a Post generator for every Source in this group.
     * Each returned Post is unique, and has been vetted against each Filter.
     * Each Post will also have all its initial links parsed into attached DBDownload objects.
     *
     * The generator is an async function that will return the next Post from the each Source, if one is available.
     */
    public async *getPostGenerator(state: DownloaderState|null = null) {
        const filters = await this.filters;
        const sources = (await this.sources).map(s => makeSource(s)).filter(t=>!!t);

        for (const s of sources) {
            try {
                if (state && state.shouldStop) return stop();
                if (state) state.currentSource = s.alias;
                const gen = s.find();

                yield* filterMap(gen, async (post, stop) => {
                    if (state && state.shouldStop) return stop();
                    const liveData: any = post.loadedData;
                    post = await dedupeExisting(post);
                    post.loadedData = liveData;

                    if (post.processed) {
                        return;
                    }
                    if (post instanceof DBSubmission) {
                        // In case we found a Submission already loaded as a comment's parent:
                        post.shouldProcess = true;
                    }

                    const links = await extractLinks(post);

                    for (const link of links) {
                        const dl = await DBDownload.getDownloader(post, link);

                        if (!filters.every(f => {
                            if (f.forSubmissions && post instanceof DBComment) return true;
                            if (!f.forSubmissions && post instanceof DBSubmission) return true;
                            return f.validate(post, link)
                        })) {
                            continue;
                        }

                        (await post.downloads).push(dl);
                    }

                    post.processed = true;

                    await post.save();

                    return post;
                }) as AsyncGenerator<DBSubmission | DBComment>
            } catch (err) {
                console.error(`Failed to scan Source: [${s.alias}]`, err);
                sendError(`Failed to scan Source: [${s.alias}] ${err.message}`);
            }
        }
    }

    /**
     * When this group needs to be sent to the client, it can be encoded suitably for serialization here.
     */
    async toSimpleObject(): Promise<SourceGroupInterface> { // TODO: Unit test.
        const r: any = {};

        for (const k in this) {
            if (!this.hasOwnProperty(k)) {
                continue
            }
            r[k] = await this[k];
        }

        r.sources = await this.sources;
        r.filters = await this.filters;

        return r;
    }
}

/**
 * Returns either the preexisting Post within the DB, or the same object it was passed.
 */
async function dedupeExisting(post: DBPost) {
    return (await forkPost(post,
        c => DBComment.findOne({id: c.id}),
        s => DBSubmission.findOne({ id: s.id})
    )) || post;
}
