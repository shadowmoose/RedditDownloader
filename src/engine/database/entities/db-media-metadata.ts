import {Column, Entity, Index, JoinColumn, OneToOne, PrimaryGeneratedColumn} from "typeorm";
import {DBEntity} from "./db-entity";
import {ParsedMediaMetadata} from "../../../shared/search-interfaces";
import DBFile from "./db-file";


@Entity({ name: 'media_metadata' })
export default class DBMediaMetadata extends DBEntity implements ParsedMediaMetadata {
    @PrimaryGeneratedColumn()
    id!: number;

    @OneToOne(() => DBFile)
    @JoinColumn()
    @Index()
    parentFile!: Promise<DBFile>;

    @Column({ type: 'text', nullable: true })
    @Index()
    audioCodec!: string | null;

    @Column({ type: 'text', nullable: true })
    videoCodec!: string | null;

    @Column({ type: 'double', nullable: true })
    bitrate!: number | null;

    @Column({ type: 'double', nullable: true })
    duration!: number | null;

    @Column({ type: 'double', nullable: true })
    height!: number | null;

    @Column({ type: 'double', nullable: true })
    width!: number | null;

    @Column({ type: 'text', nullable: true })
    originalMediaTitle!: string | null;
}
