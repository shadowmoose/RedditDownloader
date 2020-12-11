import {Entity, Column, PrimaryGeneratedColumn, Index, ManyToOne} from 'typeorm';
import {DBEntity} from "./db-entity";
import DBSourceGroup from "./db-source-group";

@Entity({ name: 'sources' })
export default class DBSource extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column({length: 15, nullable: false})
    type!: string;

    @ManyToOne(() => DBSourceGroup, src => src.sources, { nullable: false})
    @Index()
    sourceGroup!: Promise<DBSourceGroup>;

    @Column({ length: 36 })
    name!: string;

    @Column({ type: 'text', nullable: false, default: '' })
    dataJSON!: string;

    get data () {
        return JSON.parse(this.dataJSON)
    }

    set data (val: any) {
        this.dataJSON =  JSON.stringify(val)
    }
}
