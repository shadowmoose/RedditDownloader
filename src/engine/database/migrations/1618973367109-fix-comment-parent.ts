import {MigrationInterface, QueryRunner} from "typeorm";

export class fixCommentParent1618973367109 implements MigrationInterface {
    name = 'fixCommentParent1618973367109'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_e505fea3909af1657e54bc3049"`);
        await queryRunner.query(`DROP INDEX "IDX_4875672591221a61ace66f2d4f"`);
        await queryRunner.query(`CREATE TABLE "temporary_comments" ("id" varchar PRIMARY KEY NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "permaLink" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "parentSubmissionId" varchar, "parentCommentId" varchar, "fromPushshift" boolean NOT NULL DEFAULT (0), CONSTRAINT "FK_e505fea3909af1657e54bc30494" FOREIGN KEY ("parentSubmissionId") REFERENCES "submissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_4875672591221a61ace66f2d4f9" FOREIGN KEY ("parentCommentId") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "temporary_comments"("id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "permaLink", "processed", "parentSubmissionId", "parentCommentId", "fromPushshift") SELECT "id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "permaLink", "processed", "parentSubmissionId", "parentCommentId", "fromPushshift" FROM "comments"`);
        await queryRunner.query(`DROP TABLE "comments"`);
        await queryRunner.query(`ALTER TABLE "temporary_comments" RENAME TO "comments"`);
        await queryRunner.query(`CREATE INDEX "IDX_e505fea3909af1657e54bc3049" ON "comments" ("parentSubmissionId") `);
        await queryRunner.query(`CREATE INDEX "IDX_4875672591221a61ace66f2d4f" ON "comments" ("parentCommentId") `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_4875672591221a61ace66f2d4f"`);
        await queryRunner.query(`DROP INDEX "IDX_e505fea3909af1657e54bc3049"`);
        await queryRunner.query(`ALTER TABLE "comments" RENAME TO "temporary_comments"`);
        await queryRunner.query(`CREATE TABLE "comments" ("id" varchar PRIMARY KEY NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "parentRedditID" varchar NOT NULL, "permaLink" varchar NOT NULL, "rootSubmissionID" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "parentSubmissionId" varchar, "parentCommentId" varchar, "fromPushshift" boolean NOT NULL DEFAULT (0), CONSTRAINT "FK_e505fea3909af1657e54bc30494" FOREIGN KEY ("parentSubmissionId") REFERENCES "submissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_4875672591221a61ace66f2d4f9" FOREIGN KEY ("parentCommentId") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "comments"("id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "permaLink", "processed", "parentSubmissionId", "parentCommentId", "fromPushshift") SELECT "id", "author", "subreddit", "selfText", "score", "createdUTC", "firstFoundUTC", "permaLink", "processed", "parentSubmissionId", "parentCommentId", "fromPushshift" FROM "temporary_comments"`);
        await queryRunner.query(`DROP TABLE "temporary_comments"`);
        await queryRunner.query(`CREATE INDEX "IDX_4875672591221a61ace66f2d4f" ON "comments" ("parentCommentId") `);
        await queryRunner.query(`CREATE INDEX "IDX_e505fea3909af1657e54bc3049" ON "comments" ("parentSubmissionId") `);
    }
}
