
module.exports = {
	type: "better-sqlite3",
	database: `manifest.sqlite`,  // TODO: Set this once a standard local DB exists.
	entities: ['src/db/entities'],
	migrationsTableName: "migrations",
	migrations: ["src/database/migrations/*.js"],
	synchronize: true,
	cli: {
		migrationsDir: "src/database/migrations/"
	}
}
