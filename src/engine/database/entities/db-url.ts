import {
    Entity,
    Column,
    ManyToOne,
    Index,
    PrimaryGeneratedColumn,
    OneToMany
} from 'typeorm';
import {DBEntity} from "./db-entity";
import DBFile from "./db-file";
import DBDownload from "./db-download";

@Entity({ name: 'urls' })
export default class DBUrl extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    @Index({ unique: true })
    address!: string;

    @Column()
    handler!: string;

    @Column({ default: false })
    processed!: boolean;

    @Column({ default: false })
    failed!: boolean;

    @Column({ type: 'text', default: null, nullable: true })
    failureReason!: string|null;

    @Column({ default: 0 })
    completedUTC!: number;

    @ManyToOne(() => DBFile, comm => comm.urls, { nullable: true, cascade: true })
    @Index()
    file!: Promise<DBFile|null>;

    @OneToMany(() => DBDownload, dl => dl.url)
    downloads!: Promise<DBDownload[]>;

    /**
     * Find or build a DBUrl object for the given URL string.
     */
    static async dedupeURL(address: string) {
        return (await DBUrl.findOne({address})) || DBUrl.build({
            completedUTC: 0,
            failed: false,
            failureReason: null,
            handler: "",
            processed: false,
            address
        });
    }
}

