import {
    Entity,
    Column,
    ManyToOne,
    Index,
    PrimaryGeneratedColumn,
    EventSubscriber,
    EntitySubscriberInterface, InsertEvent
} from 'typeorm';
import DBSubmission from "./db-submission";
import DBComment from "./db-comment";
import {DBEntity} from "./db-entity";
import {DBPost, forkPost} from "../db";
import DBUrl from "./db-url";
import {DownloadProgress} from "../../util/state";

@Entity({ name: 'downloads' })
export default class DBDownload extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    /**
     * By default, a random UUID. If more URLs are located during processing, they should inherit this ID.
     */
    @Column({type: 'text', nullable: true})
    @Index()
    albumID!: string|null;

    @Column({default: false})
    isAlbumParent!: boolean;

    @ManyToOne(() => DBSubmission, sub => sub.downloads, { nullable: true })
    @Index()
    parentSubmission!: Promise<DBSubmission>;

    @ManyToOne(() => DBComment, comm => comm.downloads, { nullable: true })
    @Index()
    parentComment!: Promise<DBComment>;

    @ManyToOne(() => DBUrl, comm => comm.downloads, { nullable: true, cascade: true })
    @Index()
    url!: DBUrl;

    progress?: DownloadProgress;

    async getDBParent(): Promise<DBPost> {
        const p = await this.parentSubmission;
        return p || await this.parentComment;
    }

    /**
     * Creates/Finds a DBDownload instance, using the given URL (and optionally album).
     *
     * The returned Downloads will always be backed by a single global DBUrl+DBFile,
     * but the DBDownload itself may be new - and exists per-album.
     *
     * Does not save automatically.
     */
    static async getDownloader(post: DBPost, url: string, albumID?: string) {
        for (const dl of await post.downloads) {
            if (albumID && dl.albumID !== albumID) continue;
            if (dl.url.address === url) {
                return dl;
            }
        }
        // No matching Downloader. Add new one:
        const u = await DBUrl.dedupeURL(url);
        const newDL = DBDownload.build({
            albumID: albumID || null,
            isAlbumParent: false,
            progress: undefined,
            url: u
        });
        await forkPost(post,
            c => newDL.parentComment = Promise.resolve(c),
            s => newDL.parentSubmission = Promise.resolve(s)
        )
        return newDL;
    }
}


/**
 * Subscribable static emitter for all new, *unprocessed* DBDownloads.
 * Emits after each DBDownload is saved to the database.
 */
@EventSubscriber()
export class DownloadSubscriber implements EntitySubscriberInterface<DBDownload> {
    private static waiting: ((url: DBDownload|undefined)=>void)[] = [];

    listenTo() {
        return DBDownload;
    }

    afterInsert(event: InsertEvent<DBDownload>) {
        if (event.entity.url.processed) return;
        let cb = DownloadSubscriber.waiting.shift();
        if (cb) cb(event.entity);
    }

    /**
     * Wait for a new *unprocessed* DBUrl to be saved. Hands out new entities in the order that they were requested.
     *
     * Will only return `undefined` when {@link flush} is called.
     */
    public static awaitNew() {
        let r: any, err: any;
        const prom = new Promise<DBDownload|undefined>((res, rej) => {
            r = res;
            err = rej;
        });
        DownloadSubscriber.waiting.push(r);
        return prom;
    }

    /**
     * Return `undefined` to all pending listeners.
     */
    public static flush() {
        let cb;
        while (cb = this.waiting.shift()) cb(undefined);
    }
}
