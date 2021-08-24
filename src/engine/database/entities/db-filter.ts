import {Column, Entity, Index, ManyToOne, PrimaryGeneratedColumn} from 'typeorm';
import {DBEntity} from "./db-entity";
import DBSourceGroup from "./db-source-group";
import {DBPost} from "../db";
import FilterInterface, {ComparatorKeyTypes, FilterComparatorFunctions} from "../../../shared/filter-interface";


@Entity({ name: 'filters' })
export default class DBFilter extends DBEntity implements FilterInterface {
    @PrimaryGeneratedColumn()
    id!: number;

    @ManyToOne(() => DBSourceGroup, src => src.filters, { nullable: true})
    @Index()
    sourceGroup!: Promise<DBSourceGroup>;

    @Column()
    forSubmissions!: boolean;

    /** If true, Posts only pass validation when it does not match the filter criteria. */
    @Column({default: false})
    negativeMatch!: boolean;

    @Column({ length: 20 })
    field!: string;

    @Column({ type: 'varchar', length: 2 })
    comparator!: ComparatorKeyTypes;

    @Column({ type: 'text' })
    valueJSON!: string;

    get value () {
        return JSON.parse(this.valueJSON)
    }

    set value (val: any) {
        this.valueJSON =  JSON.stringify(val)
    }

    validate (post: DBPost, url?: string): boolean {
        const comp = FilterComparatorFunctions[this.comparator];
        if (!comp) throw Error(`Invalid comparator value for filter: "${this.comparator}"!`)
        // @ts-ignore
        const val = this.field === 'url' ? url : post[this.field];
        const valid = comp(val, this.value)
        return (!this.negativeMatch && valid) || (this.negativeMatch && !valid);
    }
}

