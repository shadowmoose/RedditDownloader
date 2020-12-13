import "reflect-metadata";
import {Connection, createConnection} from "typeorm";
import { envDataPath } from "../util/paths";
import DBSubmission from "./entities/db-submission";
import DBComment from "./entities/db-comment";
import DBDownload, {DownloadSubscriber} from "./entities/db-download";
import DBFile from "./entities/db-file";
import DBFilter from "./entities/db-filter";
import DBSetting from "./entities/db-setting";
import DBSourceGroup from "./entities/db-source-group";
import DBSource from "./entities/db-source";
import DBUrl from "./entities/db-url";

let _connection: Connection|null;

export async function makeDB() {
    if (_connection) return _connection;

    return createConnection({
        type: "better-sqlite3",
        database: envDataPath(`manifest.sqlite`),
        entities: [DBSubmission, DBComment, DBDownload, DBFile, DBFilter, DBSetting, DBSourceGroup, DBSource, DBUrl],
        logging: false,
        migrationsTransactionMode: 'all',
        migrationsRun: true,
        migrationsTableName: "migrations",
        migrations: [],  // Add migration classes here.
        subscribers: [DownloadSubscriber],
    }).then(async (connection: Connection) => {
        // here you can start to work with your entities
        await connection.query('VACUUM');
        await connection.synchronize();
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
