const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');

module.exports = {
	mode: 'development',
	entry: path.resolve(__dirname, './src/app/renderer.tsx'),
	target: 'web', // or use 'electron-renderer'
	devtool: 'source-map',
	devServer: {
		contentBase: path.join(__dirname, 'dist/renderer.js'),
		compress: true,
		port: 9000,
		writeToDisk: true
	},
	module: {
		rules: [
			{
				test: /\.ts(x?)$/,
				use: [{ loader: 'ts-loader' }]
			},
			{
				test: /\.s[ac]ss$/i,
				use: [
					'style-loader',
					'css-loader',
					'sass-loader',
				],
			}
		]
	},
	output: {
		path: path.resolve(__dirname + '/dist'),
		filename: 'renderer.js'
	},
	plugins: [
		new HtmlWebpackPlugin({
			template: './src/app/index.html'
		})
	],
	resolve: {
		extensions: [".ts", ".tsx", ".js", ".jsx", ".scss", ".css"]
	},
};
