import {Entity, Column, PrimaryGeneratedColumn, OneToMany, Index} from 'typeorm';
import {DBEntity} from "./db-entity";
import DBUrl from "./db-url";


@Entity({ name: 'files' })
export default class DBFile extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column({ unique: true })
    path!: string;

    @Column()
    mimeType!: string;

    @Column()
    size!: number;

    @OneToMany(() => DBUrl, dl => dl.file)
    urls!: Promise<DBUrl[]>;

    @Column({type: 'varchar', length: 64})
    shaHash!: string;

    @Column({type: 'varchar', nullable: true})
    dHash: string|null = null;
    @Column({type: 'varchar', nullable: true})
    @Index()
    hash1: string|null = null;
    @Column({type: 'varchar', nullable: true})
    @Index()
    hash2: string|null = null;
    @Column({type: 'varchar', nullable: true})
    @Index()
    hash3: string|null = null;
    @Column({type: 'varchar', nullable: true})
    @Index()
    hash4: string|null = null;
}
