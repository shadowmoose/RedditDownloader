import snoowrap from 'snoowrap';
import {Entity, Column, PrimaryColumn, ManyToOne, OneToMany, Index} from 'typeorm';
import {picker} from "../../reddit/snoo";
import * as ps from '../../reddit/pushshift';
import DBSubmission from "./db-submission";
import DBDownload from "./db-download";
import {DBEntity} from "./db-entity";
import {PsComment} from "../../reddit/pushshift";
import * as snoo from "../../reddit/snoo";
import {CommentInterface} from "../../../shared/comment-interface";

@Entity({ name: 'comments' })
export default class DBComment extends DBEntity implements CommentInterface{
    @PrimaryColumn()
    id!: string;

    @Column()
    author!: string;  // Maybe split this into an "Authors" table?

    @Column()
    subreddit!: string;

    @Column({ type: "text" })
    selfText!: string;

    @Column()
    score!: number;

    /** Creation time, in milliseconds. */
    @Column()
    createdUTC!: number;

    @Column()
    firstFoundUTC!: number;

    @Column()
    permaLink!: string;

    @Column({ default: false })
    processed!: boolean;

    @Column({ default: false })
    fromPushshift!: boolean;

    @ManyToOne(() => DBSubmission, sub => sub.children, { nullable: true})
    @Index()
    parentSubmission!: Promise<DBSubmission>;

    @ManyToOne(() => DBComment, sub => sub.children, { nullable: true})
    @Index()
    parentComment!: Promise<DBComment>;

    @OneToMany(() => DBComment, comm => comm.parentComment, {cascade: true})
    children!: Promise<DBComment[]>;

    @OneToMany(() => DBDownload, dl => dl.parentComment, {cascade: true})
    downloads!: Promise<DBDownload[]>;

    loadedData?: snoowrap.Comment|PsComment;

    /**
     * Find a DBSubmission using the given ID.
     * If the submission is not stored locally, loads the submission from Reddit and saves it in the DB.
     */
    static async getRootSubmission(id: string) {
        let loc: DBSubmission|void = await DBSubmission.findOne({id});
        if (!loc) {
            loc = await snoo.getSubmission(id).catch(() => {}) || await ps.getSubmission(id).catch(() => {});
            if (loc) loc.shouldProcess = false;
        }

        if (!loc) throw Error(`Unable to load a comment's root submission: ${id}`);

        return loc.save();
    }

    static async fromRedditComment(comment: snoowrap.Comment): Promise<DBComment> {
        return picker(comment, ['name', 'subreddit_name_prefixed', 'body', 'score', 'created_utc', 'author', 'permalink', 'parent_id', 'link_id']).then(async c => {
            const parSub = await this.getRootSubmission(c.link_id);

            return DBComment.build({
                id: c.name,
                author: c.author.name,
                createdUTC: c.created_utc*1000,
                firstFoundUTC: Date.now(),
                permaLink: c.permalink,
                processed: false,
                score: c.score,
                selfText: c.body,
                subreddit: c.subreddit_name_prefixed.replace(/^\/?r\//, ''),
                loadedData: comment,
                downloads: Promise.resolve([]),
                fromPushshift: false,
                parentSubmission: Promise.resolve(parSub)
            });
        })
    }

    static async fromPushShiftComment(comment: PsComment): Promise<DBComment> {
        const parSub = await this.getRootSubmission(comment.link_id);

        return DBComment.build({
            id: comment.id,
            author: comment.author,
            createdUTC: comment.created_utc*1000,
            firstFoundUTC: Date.now(),
            permaLink: comment.permalink,
            processed: false,
            score: comment.score,
            selfText: comment.body,
            subreddit: comment.subreddit,
            loadedData: comment,
            downloads: Promise.resolve([]),
            fromPushshift: true,
            parentSubmission: Promise.resolve(parSub)
        });
    }
}
