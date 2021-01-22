const pkg = require('./package.json');


module.exports = {
	packagerConfig: {
		// Leave extension off, autocompleted. https://electron.github.io/electron-packager/master/interfaces/electronpackager.options.html#icon
		icon: "src/app/static/logo"
	},
	electronRebuildConfig: {
		onlyModules: ["better-sqlite3"]
	},
	makers: [
		{
			name: "@electron-forge/maker-squirrel",
			config: {
				name: pkg.name
			}
		},
		{
			name: "@electron-forge/maker-zip",
			platforms: [
				"darwin"
			]
		},
		{
			name: "@electron-forge/maker-deb",
			config: {}
		},
		{
			name: "@electron-forge/maker-rpm",
			config: {}
		}
	],
	publishers: [
		{
			name: '@electron-forge/publisher-github',
			config: {
				repository: {
					owner: process.env.GITHUB_OWNER,
					name: process.env.GITHUB_PROJECT_NAME
				},
				prerelease: true
			}
		}
	],
	plugins: [
		[
			"@electron-forge/plugin-webpack",
			{
				"mainConfig": "./webpack.main.config.js",
				"renderer": {
					"config": "./webpack.renderer.config.js",
					"entryPoints": [
						{
							"html": "./src/app/index.html",
							"js": "./src/app/renderer.tsx",
							"name": "main_window"
						}
					]
				}
			}
		]
	]
}
