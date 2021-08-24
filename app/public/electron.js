const { app, BrowserWindow } = require('electron');
const server = require('../../src/engine/webserver/web-server');
const windowUrl = `http://localhost:3000`;

let mainWindow;
async function createWindow() {
	const s = await server.startServer();
	mainWindow = new BrowserWindow({
		width: 800,
		height: 600
	});
	mainWindow.loadURL(windowUrl);
	mainWindow.on(`closed`, () => (mainWindow = null));
}

app.on(`ready`, createWindow);

app.on(`window-all-closed`, () => {
	if (process.platform !== `darwin`) {
		app.quit();
	}
});

app.on(`activate`, () => {
	if (mainWindow === null) {
		createWindow();
	}
});
