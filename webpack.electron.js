const nodeExternals = require('webpack-node-externals');

module.exports = {
	// Build Mode
	mode: 'development',
	// Electron Entrypoint
	entry: './src/app/main.ts',
	target: 'electron-main',
	module: {
		rules: [
			{
				test: /\.ts$/,
				use: [{ loader: 'ts-loader' }]
			},
			{
				test: /\.node$/,
				loader: 'node-loader',
			},
		]
	},
	output: {
		path: __dirname + '/dist',
		filename: 'main.js'
	},
	resolve: {
		extensions: [".ts", ".tsx", ".js", ".jsx", ".scss", ".css"]
	},
	externals: [nodeExternals()],
}
