import {Entity, Column, PrimaryGeneratedColumn, Index} from 'typeorm';
import {DBEntity} from "./db-entity";

/**
 * Track symlinks RMD has created, just to avoid recursion errors.
 */
@Entity({ name: 'symlinks' })
export default class DBSymLink extends DBEntity {
    @PrimaryGeneratedColumn()
    id!: number;

    /** The relative file path that this symlink exists at. */
    @Column({ type: 'text' })
    location!: string;

    /** The relative file path that this symlink redirects to. */
    @Column({ type: 'text' })
    @Index()
    target!: string;
}
