const fs = require('fs');

const outDir = './dist/engine/database/';

if (!fs.existsSync(outDir)) throw Error('The configured database directory in ormconfig.js does not exist.')

console.log('Using valid orm config file.')

module.exports = {
	type: "better-sqlite3",
	database: `./downloads/.rmd-data/manifest.sqlite`,  // TODO: Set this once a standard local DB exists.
	entities: [`${outDir}/entities/**.*`],
	migrationsTableName: "migrations",
	migrations: [`${outDir}/migrations/*.js`],
	synchronize: false,
	cli: {
		migrationsDir: `${outDir}/migrations/`
	}
}
