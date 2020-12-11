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
    public async *getPostGenerator() {
        const filters = await this.filters;
        const sources = (await this.sources).map(s => makeSource(s)).filter(t=>!!t);

        for (const s of sources) {
            const gen = s!.find();

            yield* filterMap(gen, async post => {
                post = await checkExisting(post);

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

                return post;
            }) as AsyncGenerator<DBSubmission | DBComment>
        }
    }
}

/**
 * Returns either the preexisting Post within the DB, or the same object it was passed.
 */
async function checkExisting(post: DBPost) {
    return (await forkPost(post,
        c => DBComment.findOne({id: c.id}),
        s => DBSubmission.findOne({ id: s.id})
    )) || post;
}
