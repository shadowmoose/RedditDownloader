import "reflect-metadata";
import {Connection, createConnection} from "typeorm";
import { envDataPath } from "../core/paths";
import DBSubmission from "./entities/db-submission";
import DBComment from "./entities/db-comment";
import DBDownload, {DownloadSubscriber} from "./entities/db-download";
import DBFile from "./entities/db-file";
import DBFilter from "./entities/db-filter";
import DBSetting from "./entities/db-setting";
import DBSourceGroup from "./entities/db-source-group";
import DBSource from "./entities/db-source";
import DBUrl from "./entities/db-url";
import {initial1613378705882} from "./migrations/1613378705882-initial";
import {psTagCol1615799411768} from "./migrations/1615799411768-ps-tag-col";
import {dlAlbumIndex1615805733346} from "./migrations/1615805733346-dl-album-index";
import {stringPaddedIndex1615868441239} from "./migrations/1615868441239-string-padded-index";
import DBSymLink from "./entities/db-symlink";
import {addSymlinks1615947913892} from "./migrations/1615947913892-add-symlinks";
import {addDirFlag1616042478022} from "./migrations/1616042478022-add-dir-flag";
import {fileIsAlbum1616318709797} from "./migrations/1616318709797-file-is-album";
import {addInvertedFilter1617069277622} from "./migrations/1617069277622-add-inverted-filter";
import {fixCommentParent1618973367109} from "./migrations/1618973367109-fix-comment-parent";
import {addSourceCascade1629767914963} from "./migrations/1629767914963-add-source-cascade";
import {addAllDeleteCascades1629768495254} from "./migrations/1629768495254-add-all-delete-cascades";

let _connection: Connection|null;

export async function makeDB() {
    if (_connection) return _connection;

    return createConnection({
        type: "better-sqlite3",
        database: envDataPath(`manifest.sqlite`),
        entities: [DBSubmission, DBComment, DBDownload, DBFile, DBFilter, DBSetting, DBSourceGroup, DBSource, DBUrl, DBSymLink],
        logging: false,
        synchronize: false,
        migrationsTransactionMode: 'all',
        migrationsRun: false,
        migrationsTableName: "migrations",
        migrations: [
            initial1613378705882,
            psTagCol1615799411768,
            dlAlbumIndex1615805733346,
            stringPaddedIndex1615868441239,
            addSymlinks1615947913892,
            addDirFlag1616042478022,
            fileIsAlbum1616318709797,
            addInvertedFilter1617069277622,
            fixCommentParent1618973367109,
            addSourceCascade1629767914963,
            addAllDeleteCascades1629768495254,
        ],  // Add migration classes here.
        subscribers: [DownloadSubscriber],
    }).then(async (connection: Connection) => {
        await connection.query('PRAGMA foreign_keys=OFF');  // TypeORM sucks at migrations, so disable key checks until after.
        // here you can start to work with your entities
        await connection.runMigrations({
            transaction: 'all'
        });
        await connection.query('PRAGMA foreign_keys=ON');
        await connection.query('VACUUM');
        _connection = connection;
        return connection;
    });
}

/**  Generic type for things that can be Comments or Submissions. */
export type DBPost = DBComment | DBSubmission;

/**
 * Simplifies processing Comments & Submissions by splitting the input into the result of either function,
 * based off its class.
 * @param post The Comment/Submission to check.
 * @param comment A callback if this Post is a Comment.
 * @param submission A callback if this Post is a Submission.
 */
export function forkPost<C,S>(post: DBPost, comment: (cmm: DBComment)=>C, submission: (s: DBSubmission)=>S): C|S {
    if (post instanceof  DBComment) {
        return comment(post);
    } else {
        return submission(post);
    }
}
