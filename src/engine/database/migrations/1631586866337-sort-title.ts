import {MigrationInterface, QueryRunner} from "typeorm";

export class sortTitle1631586866337 implements MigrationInterface {
    name = 'sortTitle1631586866337'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_fe08c55edb19ba680622ac3c4a"`);
        await queryRunner.query(`DROP INDEX "IDX_5766e2995ae9630654e73d4b6f"`);
        await queryRunner.query(`CREATE TABLE "temporary_submissions" ("id" varchar PRIMARY KEY NOT NULL, "title" text NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "isSelf" boolean NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "nsfw" boolean NOT NULL, "flairText" text, "processed" boolean NOT NULL DEFAULT (0), "shouldProcess" boolean NOT NULL DEFAULT (1), "fromPushshift" boolean NOT NULL DEFAULT (0), "sortTitle" text NOT NULL)`);
        await queryRunner.query(`INSERT INTO "temporary_submissions" ("id", "title", "sortTitle", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "nsfw", "flairText", "processed", "shouldProcess", "fromPushshift") SELECT "id", "title", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "nsfw", "flairText", "processed", "shouldProcess", "fromPushshift" FROM "submissions"`);

        const existing: any[] = await queryRunner.query("select id, title from submissions");
        for (const ex of existing) {
            await queryRunner.query(`UPDATE temporary_submissions SET sortTitle=? WHERE id=?`, [ex.title.replace(/\W/gm, '').trim().toUpperCase(), ex.id]);
        }

        await queryRunner.query(`DROP TABLE "submissions"`);
        await queryRunner.query(`ALTER TABLE "temporary_submissions" RENAME TO "submissions"`);
        await queryRunner.query(`CREATE INDEX "IDX_136e3e5a2c779346f2d0be09ad" ON "media_metadata" ("parentFileId") `);
        await queryRunner.query(`CREATE INDEX "IDX_4a60a9832d03ce19225bd611f1" ON "media_metadata" ("audioCodec") `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_4a60a9832d03ce19225bd611f1"`);
        await queryRunner.query(`DROP INDEX "IDX_136e3e5a2c779346f2d0be09ad"`);
        await queryRunner.query(`ALTER TABLE "submissions" RENAME TO "temporary_submissions"`);
        await queryRunner.query(`CREATE TABLE "submissions" ("id" varchar PRIMARY KEY NOT NULL, "title" text NOT NULL, "author" varchar NOT NULL, "subreddit" varchar NOT NULL, "selfText" text NOT NULL, "score" integer NOT NULL, "isSelf" boolean NOT NULL, "createdUTC" integer NOT NULL, "firstFoundUTC" integer NOT NULL, "nsfw" boolean NOT NULL, "flairText" text, "processed" boolean NOT NULL DEFAULT (0), "shouldProcess" boolean NOT NULL DEFAULT (1), "fromPushshift" boolean NOT NULL DEFAULT (0))`);
        await queryRunner.query(`INSERT INTO "submissions"("id", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "nsfw", "flairText", "processed", "shouldProcess", "fromPushshift") SELECT "id", "title", "author", "subreddit", "selfText", "score", "isSelf", "createdUTC", "firstFoundUTC", "nsfw", "flairText", "processed", "shouldProcess", "fromPushshift" FROM "temporary_submissions"`);
        await queryRunner.query(`DROP TABLE "temporary_submissions"`);
        await queryRunner.query(`CREATE INDEX "IDX_5766e2995ae9630654e73d4b6f" ON "media_metadata" ("parentFileId") `);
        await queryRunner.query(`CREATE INDEX "IDX_fe08c55edb19ba680622ac3c4a" ON "media_metadata" ("audioCodec") `);
    }

}
