import { app, BrowserWindow } from 'electron';
import isDev from 'electron-is-dev';
import {startServer} from "../engine/webserver/web-server"; // New Import


const createWindow = async () => {
    const res = await startServer();

    let win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: false
        }
    });
    console.log(isDev);
    win.loadURL(
        isDev
            ? 'http://localhost:9000/dist/index.html'
            : `file://${app.getAppPath()}/index.html`,
    );
}

app.on('ready', createWindow);
