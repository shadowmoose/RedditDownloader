import snoowrap from 'snoowrap';
import {Entity, Column, PrimaryColumn, ManyToOne, OneToMany, Index} from 'typeorm';
import {getSubmission, picker} from "../../reddit/snoo";
import DBSubmission from "./db-submission";
import DBDownload from "./db-download";
import {DBEntity} from "./db-entity";

@Entity({ name: 'comments' })
export default class DBComment extends DBEntity {
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

    @Column()
    createdUTC!: number;

    @Column()
    firstFoundUTC!: number;

    @Column()
    parentRedditID!: string;

    @Column()
    permaLink!: string;

    @Column()
    rootSubmissionID!: string;

    @Column({ default: false })
    processed!: boolean;

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

    loadedData?: snoowrap.Comment;

    /**
     * Find this comment's root submission.
     * If the submission is not stored locally, loads the submission from Reddit and saves it in the DB.
     */
    async getRootSubmission(): Promise<DBSubmission|null> {
        let loc = await DBSubmission.findOne({id: this.rootSubmissionID});
        if (!loc) {
            loc = await getSubmission(this.rootSubmissionID); // TODO: PushShift as a backup.
            if (loc) {
                loc.shouldProcess = false;
                await loc.save()
            }
        }
        return loc ;
    }

    static async fromRedditComment(comment: snoowrap.Comment): Promise<DBComment> {
        return picker(comment, ['name', 'subreddit_name_prefixed', 'body', 'score', 'created_utc', 'author', 'permalink', 'parent_id', 'link_id']).then(c => {
            return DBComment.build({
                id: c.name,
                author: c.author.name,
                createdUTC: c.created_utc*1000,
                firstFoundUTC: Date.now(),
                parentRedditID: c.parent_id,
                permaLink: c.permalink,
                processed: false,
                rootSubmissionID: c.link_id,
                score: c.score,
                selfText: c.body,
                subreddit: c.subreddit_name_prefixed.replace(/^\/?r\//, ''),
                loadedData: comment,
                downloads: Promise.resolve([])
            });
        })
    }
}
