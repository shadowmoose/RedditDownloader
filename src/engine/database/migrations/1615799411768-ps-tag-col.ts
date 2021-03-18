import {MigrationInterface, QueryRunner} from "typeorm";

export class psTagCol1615799411768 implements MigrationInterface {
    name = 'psTagCol1615799411768'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "temporary_submissions" ("id" varchar PRIMARY KEY NOT NULL, "title" text NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "isSelf" boolean NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "over18" boolean NOT NULL, "flairText" text, "processed" boolean NOT NULL DEFAULT (0), "shouldProcess" boolean NOT NULL DEFAULT (1), "fromPushshift" boolean NOT NULL DEFAULT (0))`);
        await queryRunner.query(`INSERT INTO "temporary_submissions"("id", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "over18", "flairText", "processed", "shouldProcess") SELECT "id", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "over18", "flairText", "processed", "shouldProcess" FROM "submissions"`);
        await queryRunner.query(`DROP TABLE "submissions"`);
        await queryRunner.query(`ALTER TABLE "temporary_submissions" RENAME TO "submissions"`);
        await queryRunner.query(`DROP INDEX "IDX_4875672591221a61ace66f2d4f"`);
        await queryRunner.query(`DROP INDEX "IDX_e505fea3909af1657e54bc3049"`);
        await queryRunner.query(`CREATE TABLE "temporary_comments" ("id" varchar PRIMARY KEY NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "parentRedditID" varchar NOT NULL, "permaLink" varchar NOT NULL, "rootSubmissionID" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "parentSubmissionId" varchar, "parentCommentId" varchar, "fromPushshift" boolean NOT NULL DEFAULT (0), CONSTRAINT "FK_4875672591221a61ace66f2d4f9" FOREIGN KEY ("parentCommentId") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_e505fea3909af1657e54bc30494" FOREIGN KEY ("parentSubmissionId") REFERENCES "submissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "temporary_comments"("id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "parentRedditID", "permaLink", "rootSubmissionID", "processed", "parentSubmissionId", "parentCommentId") SELECT "id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "parentRedditID", "permaLink", "rootSubmissionID", "processed", "parentSubmissionId", "parentCommentId" FROM "comments"`);
        await queryRunner.query(`DROP TABLE "comments"`);
        await queryRunner.query(`ALTER TABLE "temporary_comments" RENAME TO "comments"`);
        await queryRunner.query(`CREATE INDEX "IDX_4875672591221a61ace66f2d4f" ON "comments" ("parentCommentId") `);
        await queryRunner.query(`CREATE INDEX "IDX_e505fea3909af1657e54bc3049" ON "comments" ("parentSubmissionId") `);
        await queryRunner.query(`DROP INDEX "IDX_b911a51a0637a4e27e0dd1ce23"`);
        await queryRunner.query(`DROP INDEX "IDX_792ca9643eaf7971a9dd1112a5"`);
        await queryRunner.query(`CREATE TABLE "temporary_urls" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "address" varchar NOT NULL, "handler" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "failed" boolean NOT NULL DEFAULT (0), "failureReason" text, "completedUTC" integer NOT NULL DEFAULT (0), "fileId" integer, CONSTRAINT "FK_b911a51a0637a4e27e0dd1ce23a" FOREIGN KEY ("fileId") REFERENCES "files" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "temporary_urls"("id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId") SELECT "id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId" FROM "urls"`);
        await queryRunner.query(`DROP TABLE "urls"`);
        await queryRunner.query(`ALTER TABLE "temporary_urls" RENAME TO "urls"`);
        await queryRunner.query(`CREATE INDEX "IDX_b911a51a0637a4e27e0dd1ce23" ON "urls" ("fileId") `);
        await queryRunner.query(`CREATE UNIQUE INDEX "IDX_792ca9643eaf7971a9dd1112a5" ON "urls" ("address") `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_792ca9643eaf7971a9dd1112a5"`);
        await queryRunner.query(`DROP INDEX "IDX_b911a51a0637a4e27e0dd1ce23"`);
        await queryRunner.query(`ALTER TABLE "urls" RENAME TO "temporary_urls"`);
        await queryRunner.query(`CREATE TABLE "urls" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "address" varchar NOT NULL, "handler" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "failed" boolean NOT NULL DEFAULT (0), "failureReason" text, "completedUTC" integer NOT NULL DEFAULT (0), "fileId" integer, CONSTRAINT "FK_b911a51a0637a4e27e0dd1ce23a" FOREIGN KEY ("fileId") REFERENCES "files" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "urls"("id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId") SELECT "id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId" FROM "temporary_urls"`);
        await queryRunner.query(`DROP TABLE "temporary_urls"`);
        await queryRunner.query(`CREATE UNIQUE INDEX "IDX_792ca9643eaf7971a9dd1112a5" ON "urls" ("address") `);
        await queryRunner.query(`CREATE INDEX "IDX_b911a51a0637a4e27e0dd1ce23" ON "urls" ("fileId") `);
        await queryRunner.query(`DROP INDEX "IDX_e505fea3909af1657e54bc3049"`);
        await queryRunner.query(`DROP INDEX "IDX_4875672591221a61ace66f2d4f"`);
        await queryRunner.query(`ALTER TABLE "comments" RENAME TO "temporary_comments"`);
        await queryRunner.query(`CREATE TABLE "comments" ("id" varchar PRIMARY KEY NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "parentRedditID" varchar NOT NULL, "permaLink" varchar NOT NULL, "rootSubmissionID" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "parentSubmissionId" varchar, "parentCommentId" varchar, CONSTRAINT "FK_4875672591221a61ace66f2d4f9" FOREIGN KEY ("parentCommentId") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_e505fea3909af1657e54bc30494" FOREIGN KEY ("parentSubmissionId") REFERENCES "submissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "comments"("id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "parentRedditID", "permaLink", "rootSubmissionID", "processed", "parentSubmissionId", "parentCommentId") SELECT "id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "parentRedditID", "permaLink", "rootSubmissionID", "processed", "parentSubmissionId", "parentCommentId" FROM "temporary_comments"`);
        await queryRunner.query(`DROP TABLE "temporary_comments"`);
        await queryRunner.query(`CREATE INDEX "IDX_e505fea3909af1657e54bc3049" ON "comments" ("parentSubmissionId") `);
        await queryRunner.query(`CREATE INDEX "IDX_4875672591221a61ace66f2d4f" ON "comments" ("parentCommentId") `);
        await queryRunner.query(`ALTER TABLE "submissions" RENAME TO "temporary_submissions"`);
        await queryRunner.query(`CREATE TABLE "submissions" ("id" varchar PRIMARY KEY NOT NULL, "title" text NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "isSelf" boolean NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "over18" boolean NOT NULL, "flairText" text, "processed" boolean NOT NULL DEFAULT (0), "shouldProcess" boolean NOT NULL DEFAULT (1))`);
        await queryRunner.query(`INSERT INTO "submissions"("id", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "over18", "flairText", "processed", "shouldProcess") SELECT "id", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "over18", "flairText", "processed", "shouldProcess" FROM "temporary_submissions"`);
        await queryRunner.query(`DROP TABLE "temporary_submissions"`);
    }

}
