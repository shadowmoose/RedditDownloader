import {MigrationInterface, QueryRunner} from "typeorm";

export class fileIsAlbum1616318709797 implements MigrationInterface {
    name = 'fileIsAlbum1616318709797'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_f6abfcac75948edeaea5b22678"`);
        await queryRunner.query(`DROP INDEX "IDX_2194756621203ab8d1de83e3c7"`);
        await queryRunner.query(`DROP INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f"`);
        await queryRunner.query(`DROP INDEX "IDX_9560d52d1e438c4e75a9dade8c"`);
        await queryRunner.query(`CREATE TABLE "temporary_files" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "path" varchar NOT NULL, "mimeType" varchar NOT NULL, "size" integer NOT NULL, "shaHash" varchar(64) NOT NULL, "dHash" varchar, "hash1" varchar, "hash2" varchar, "hash3" varchar, "hash4" varchar, "isDir" boolean NOT NULL, "isAlbumFile" boolean NOT NULL, CONSTRAINT "UQ_93c04123b9642879843a20d971a" UNIQUE ("path"))`);
        await queryRunner.query(`INSERT INTO "temporary_files"("id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir") SELECT "id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir" FROM "files"`);
        await queryRunner.query(`DROP TABLE "files"`);
        await queryRunner.query(`ALTER TABLE "temporary_files" RENAME TO "files"`);
        await queryRunner.query(`CREATE INDEX "IDX_f6abfcac75948edeaea5b22678" ON "files" ("hash1") `);
        await queryRunner.query(`CREATE INDEX "IDX_2194756621203ab8d1de83e3c7" ON "files" ("hash2") `);
        await queryRunner.query(`CREATE INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f" ON "files" ("hash3") `);
        await queryRunner.query(`CREATE INDEX "IDX_9560d52d1e438c4e75a9dade8c" ON "files" ("hash4") `);
        await queryRunner.query(`DROP INDEX "IDX_792ca9643eaf7971a9dd1112a5"`);
        await queryRunner.query(`DROP INDEX "IDX_b911a51a0637a4e27e0dd1ce23"`);
        await queryRunner.query(`CREATE TABLE "temporary_urls" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "address" varchar NOT NULL, "handler" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "failed" boolean NOT NULL DEFAULT (0), "failureReason" text, "completedUTC" integer NOT NULL DEFAULT (0), "fileId" integer, CONSTRAINT "FK_b911a51a0637a4e27e0dd1ce23a" FOREIGN KEY ("fileId") REFERENCES "files" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "temporary_urls"("id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId") SELECT "id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId" FROM "urls"`);
        await queryRunner.query(`DROP TABLE "urls"`);
        await queryRunner.query(`ALTER TABLE "temporary_urls" RENAME TO "urls"`);
        await queryRunner.query(`CREATE UNIQUE INDEX "IDX_792ca9643eaf7971a9dd1112a5" ON "urls" ("address") `);
        await queryRunner.query(`CREATE INDEX "IDX_b911a51a0637a4e27e0dd1ce23" ON "urls" ("fileId") `);
        await queryRunner.query(`DROP INDEX "IDX_f6abfcac75948edeaea5b22678"`);
        await queryRunner.query(`DROP INDEX "IDX_2194756621203ab8d1de83e3c7"`);
        await queryRunner.query(`DROP INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f"`);
        await queryRunner.query(`DROP INDEX "IDX_9560d52d1e438c4e75a9dade8c"`);
        await queryRunner.query(`CREATE TABLE "temporary_files" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "path" varchar NOT NULL, "mimeType" varchar, "size" integer NOT NULL, "shaHash" varchar(64), "dHash" varchar, "hash1" varchar, "hash2" varchar, "hash3" varchar, "hash4" varchar, "isDir" boolean NOT NULL, "isAlbumFile" boolean NOT NULL, CONSTRAINT "UQ_93c04123b9642879843a20d971a" UNIQUE ("path"))`);
        await queryRunner.query(`INSERT INTO "temporary_files"("id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir", "isAlbumFile") SELECT "id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir", "isAlbumFile" FROM "files"`);
        await queryRunner.query(`DROP TABLE "files"`);
        await queryRunner.query(`ALTER TABLE "temporary_files" RENAME TO "files"`);
        await queryRunner.query(`CREATE INDEX "IDX_f6abfcac75948edeaea5b22678" ON "files" ("hash1") `);
        await queryRunner.query(`CREATE INDEX "IDX_2194756621203ab8d1de83e3c7" ON "files" ("hash2") `);
        await queryRunner.query(`CREATE INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f" ON "files" ("hash3") `);
        await queryRunner.query(`CREATE INDEX "IDX_9560d52d1e438c4e75a9dade8c" ON "files" ("hash4") `);
        await queryRunner.query(`DROP INDEX "IDX_96db2e076ee5f721b37fd2ad5f"`);
        await queryRunner.query(`DROP INDEX "IDX_5d63d7c074e60a34a228f9855d"`);
        await queryRunner.query(`DROP INDEX "IDX_eb6849e986a0678a61d97504bc"`);
        await queryRunner.query(`DROP INDEX "IDX_337604abe2c3c9ab698cc9d294"`);
        await queryRunner.query(`CREATE TABLE "temporary_downloads" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "albumID" text, "isAlbumParent" boolean NOT NULL DEFAULT (0), "parentSubmissionId" varchar, "parentCommentId" varchar, "urlId" integer, "albumPaddedIndex" varchar, CONSTRAINT "FK_96db2e076ee5f721b37fd2ad5f8" FOREIGN KEY ("urlId") REFERENCES "urls" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_5d63d7c074e60a34a228f9855de" FOREIGN KEY ("parentCommentId") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_eb6849e986a0678a61d97504bcd" FOREIGN KEY ("parentSubmissionId") REFERENCES "submissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "temporary_downloads"("id", "albumID", "isAlbumParent", "parentSubmissionId", "parentCommentId", "urlId", "albumPaddedIndex") SELECT "id", "albumID", "isAlbumParent", "parentSubmissionId", "parentCommentId", "urlId", "albumPaddedIndex" FROM "downloads"`);
        await queryRunner.query(`DROP TABLE "downloads"`);
        await queryRunner.query(`ALTER TABLE "temporary_downloads" RENAME TO "downloads"`);
        await queryRunner.query(`CREATE INDEX "IDX_96db2e076ee5f721b37fd2ad5f" ON "downloads" ("urlId") `);
        await queryRunner.query(`CREATE INDEX "IDX_5d63d7c074e60a34a228f9855d" ON "downloads" ("parentCommentId") `);
        await queryRunner.query(`CREATE INDEX "IDX_eb6849e986a0678a61d97504bc" ON "downloads" ("parentSubmissionId") `);
        await queryRunner.query(`CREATE INDEX "IDX_337604abe2c3c9ab698cc9d294" ON "downloads" ("albumID") `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_337604abe2c3c9ab698cc9d294"`);
        await queryRunner.query(`DROP INDEX "IDX_eb6849e986a0678a61d97504bc"`);
        await queryRunner.query(`DROP INDEX "IDX_5d63d7c074e60a34a228f9855d"`);
        await queryRunner.query(`DROP INDEX "IDX_96db2e076ee5f721b37fd2ad5f"`);
        await queryRunner.query(`ALTER TABLE "downloads" RENAME TO "temporary_downloads"`);
        await queryRunner.query(`CREATE TABLE "downloads" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "albumID" text, "isAlbumParent" boolean NOT NULL DEFAULT (0), "parentSubmissionId" varchar, "parentCommentId" varchar, "urlId" integer, "albumPaddedIndex" varchar, CONSTRAINT "FK_96db2e076ee5f721b37fd2ad5f8" FOREIGN KEY ("urlId") REFERENCES "urls" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_5d63d7c074e60a34a228f9855de" FOREIGN KEY ("parentCommentId") REFERENCES "comments" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION, CONSTRAINT "FK_eb6849e986a0678a61d97504bcd" FOREIGN KEY ("parentSubmissionId") REFERENCES "submissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "downloads"("id", "albumID", "isAlbumParent", "parentSubmissionId", "parentCommentId", "urlId", "albumPaddedIndex") SELECT "id", "albumID", "isAlbumParent", "parentSubmissionId", "parentCommentId", "urlId", "albumPaddedIndex" FROM "temporary_downloads"`);
        await queryRunner.query(`DROP TABLE "temporary_downloads"`);
        await queryRunner.query(`CREATE INDEX "IDX_337604abe2c3c9ab698cc9d294" ON "downloads" ("albumID") `);
        await queryRunner.query(`CREATE INDEX "IDX_eb6849e986a0678a61d97504bc" ON "downloads" ("parentSubmissionId") `);
        await queryRunner.query(`CREATE INDEX "IDX_5d63d7c074e60a34a228f9855d" ON "downloads" ("parentCommentId") `);
        await queryRunner.query(`CREATE INDEX "IDX_96db2e076ee5f721b37fd2ad5f" ON "downloads" ("urlId") `);
        await queryRunner.query(`DROP INDEX "IDX_9560d52d1e438c4e75a9dade8c"`);
        await queryRunner.query(`DROP INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f"`);
        await queryRunner.query(`DROP INDEX "IDX_2194756621203ab8d1de83e3c7"`);
        await queryRunner.query(`DROP INDEX "IDX_f6abfcac75948edeaea5b22678"`);
        await queryRunner.query(`ALTER TABLE "files" RENAME TO "temporary_files"`);
        await queryRunner.query(`CREATE TABLE "files" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "path" varchar NOT NULL, "mimeType" varchar NOT NULL, "size" integer NOT NULL, "shaHash" varchar(64) NOT NULL, "dHash" varchar, "hash1" varchar, "hash2" varchar, "hash3" varchar, "hash4" varchar, "isDir" boolean NOT NULL, "isAlbumFile" boolean NOT NULL, CONSTRAINT "UQ_93c04123b9642879843a20d971a" UNIQUE ("path"))`);
        await queryRunner.query(`INSERT INTO "files"("id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir", "isAlbumFile") SELECT "id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir", "isAlbumFile" FROM "temporary_files"`);
        await queryRunner.query(`DROP TABLE "temporary_files"`);
        await queryRunner.query(`CREATE INDEX "IDX_9560d52d1e438c4e75a9dade8c" ON "files" ("hash4") `);
        await queryRunner.query(`CREATE INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f" ON "files" ("hash3") `);
        await queryRunner.query(`CREATE INDEX "IDX_2194756621203ab8d1de83e3c7" ON "files" ("hash2") `);
        await queryRunner.query(`CREATE INDEX "IDX_f6abfcac75948edeaea5b22678" ON "files" ("hash1") `);
        await queryRunner.query(`DROP INDEX "IDX_b911a51a0637a4e27e0dd1ce23"`);
        await queryRunner.query(`DROP INDEX "IDX_792ca9643eaf7971a9dd1112a5"`);
        await queryRunner.query(`ALTER TABLE "urls" RENAME TO "temporary_urls"`);
        await queryRunner.query(`CREATE TABLE "urls" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "address" varchar NOT NULL, "handler" varchar NOT NULL, "processed" boolean NOT NULL DEFAULT (0), "failed" boolean NOT NULL DEFAULT (0), "failureReason" text, "completedUTC" integer NOT NULL DEFAULT (0), "fileId" integer, CONSTRAINT "FK_b911a51a0637a4e27e0dd1ce23a" FOREIGN KEY ("fileId") REFERENCES "files" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "urls"("id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId") SELECT "id", "address", "handler", "processed", "failed", "failureReason", "completedUTC", "fileId" FROM "temporary_urls"`);
        await queryRunner.query(`DROP TABLE "temporary_urls"`);
        await queryRunner.query(`CREATE INDEX "IDX_b911a51a0637a4e27e0dd1ce23" ON "urls" ("fileId") `);
        await queryRunner.query(`CREATE UNIQUE INDEX "IDX_792ca9643eaf7971a9dd1112a5" ON "urls" ("address") `);
        await queryRunner.query(`DROP INDEX "IDX_9560d52d1e438c4e75a9dade8c"`);
        await queryRunner.query(`DROP INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f"`);
        await queryRunner.query(`DROP INDEX "IDX_2194756621203ab8d1de83e3c7"`);
        await queryRunner.query(`DROP INDEX "IDX_f6abfcac75948edeaea5b22678"`);
        await queryRunner.query(`ALTER TABLE "files" RENAME TO "temporary_files"`);
        await queryRunner.query(`CREATE TABLE "files" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "path" varchar NOT NULL, "mimeType" varchar NOT NULL, "size" integer NOT NULL, "shaHash" varchar(64) NOT NULL, "dHash" varchar, "hash1" varchar, "hash2" varchar, "hash3" varchar, "hash4" varchar, "isDir" boolean NOT NULL, CONSTRAINT "UQ_93c04123b9642879843a20d971a" UNIQUE ("path"))`);
        await queryRunner.query(`INSERT INTO "files"("id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir") SELECT "id", "path", "mimeType", "size", "shaHash", "dHash", "hash1", "hash2", "hash3", "hash4", "isDir" FROM "temporary_files"`);
        await queryRunner.query(`DROP TABLE "temporary_files"`);
        await queryRunner.query(`CREATE INDEX "IDX_9560d52d1e438c4e75a9dade8c" ON "files" ("hash4") `);
        await queryRunner.query(`CREATE INDEX "IDX_b0bdbefd12ad3b08dcd4b1671f" ON "files" ("hash3") `);
        await queryRunner.query(`CREATE INDEX "IDX_2194756621203ab8d1de83e3c7" ON "files" ("hash2") `);
        await queryRunner.query(`CREATE INDEX "IDX_f6abfcac75948edeaea5b22678" ON "files" ("hash1") `);
    }

}
