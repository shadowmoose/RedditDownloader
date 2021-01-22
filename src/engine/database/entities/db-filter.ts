import {Entity, Column, PrimaryGeneratedColumn, Index, ManyToOne} from 'typeorm';
import {DBEntity} from "./db-entity";
import DBSourceGroup from "./db-source-group";
import DBSubmission from "./db-submission";
import DBComment from "./db-comment";


@Entity({ name: 'filters' })
export default class DBFilter extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    @ManyToOne(() => DBSourceGroup, src => src.filters, { nullable: true})
    @Index()
    sourceGroup!: Promise<DBSourceGroup>;

    @Column()
    forSubmissions!: boolean;

    @Column({ length: 20 })
    field!: string;

    @Column({ type: 'varchar', length: 2 })
    comparator!: ComparatorKeys;

    @Column({ type: 'text' })
    valueJSON!: string;

    get value () {
        return JSON.parse(this.valueJSON)
    }

    set value (val: any) {
        this.valueJSON =  JSON.stringify(val)
    }

    validate (post: DBSubmission|DBComment, url?: string): boolean {
        const comp = comparators[this.comparator];
        if (!comp) throw Error(`Invalid comparator value for filter: "${this.comparator}"!`)
        // @ts-ignore
        const val = this.field === 'url' ? url : post[this.field];
        return comp(val, this.value);
    }
}

type ComparatorKeys = '>'|'<'|'='|'re';
type Comparator = (val1: any, val2: any) => boolean;

export const comparators: Record<ComparatorKeys, Comparator> = {
    '>': (val1, val2) => {return val1 > val2},
    '<': (val1, val2) => {return val1 < val2},
    '=': (val1, val2) => {return val1 == val2},
    're': (val1, val2) => {return Boolean(`${val1}`.match(new RegExp(val2, 'gmi')))},
}
