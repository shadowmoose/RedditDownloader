import {MigrationInterface, QueryRunner} from "typeorm";

export class addInvertedFilter1617069277622 implements MigrationInterface {
    name = 'addInvertedFilter1617069277622'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_a1110777a20270c18440d32c4c"`);
        await queryRunner.query(`CREATE TABLE "temporary_filters" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "forSubmissions" boolean NOT NULL, "field" varchar(20) NOT NULL, "comparator" varchar(2) NOT NULL, "valueJSON" text NOT NULL, "sourceGroupId" integer, "negativeMatch" boolean NOT NULL DEFAULT (0), CONSTRAINT "FK_a1110777a20270c18440d32c4c3" FOREIGN KEY ("sourceGroupId") REFERENCES "source_groups" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "temporary_filters"("id", "forSubmissions", "field", "comparator", "valueJSON", "sourceGroupId") SELECT "id", "forSubmissions", "field", "comparator", "valueJSON", "sourceGroupId" FROM "filters"`);
        await queryRunner.query(`DROP TABLE "filters"`);
        await queryRunner.query(`ALTER TABLE "temporary_filters" RENAME TO "filters"`);
        await queryRunner.query(`CREATE INDEX "IDX_a1110777a20270c18440d32c4c" ON "filters" ("sourceGroupId") `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_a1110777a20270c18440d32c4c"`);
        await queryRunner.query(`ALTER TABLE "filters" RENAME TO "temporary_filters"`);
        await queryRunner.query(`CREATE TABLE "filters" ("id" integer PRIMARY KEY AUTOINCREMENT NOT NULL, "forSubmissions" boolean NOT NULL, "field" varchar(20) NOT NULL, "comparator" varchar(2) NOT NULL, "valueJSON" text NOT NULL, "sourceGroupId" integer, CONSTRAINT "FK_a1110777a20270c18440d32c4c3" FOREIGN KEY ("sourceGroupId") REFERENCES "source_groups" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION)`);
        await queryRunner.query(`INSERT INTO "filters"("id", "forSubmissions", "field", "comparator", "valueJSON", "sourceGroupId") SELECT "id", "forSubmissions", "field", "comparator", "valueJSON", "sourceGroupId" FROM "temporary_filters"`);
        await queryRunner.query(`DROP TABLE "temporary_filters"`);
        await queryRunner.query(`CREATE INDEX "IDX_a1110777a20270c18440d32c4c" ON "filters" ("sourceGroupId") `);
    }
}
