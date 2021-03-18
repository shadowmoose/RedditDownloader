import {getJSON} from "../util/http";
import * as child_process from 'child_process';
import {sharedPath} from "../util/paths";
import path from 'path';
import * as os from "os";
import axios from "axios";
import fs from 'fs';
const unzip = require('unzip-stream');

const isWin = process.platform === 'win32' || process.env.NODE_PLATFORM === 'windows';
const platform = isWin ? 'windows' : process.platform === 'darwin' ? 'osx' : 'linux';
const arch = os.arch().replace('x', '');
const ext = isWin ? '.exe':'';
export const ffmpegDir = sharedPath('bin', 'ffmpeg');
export const ffmpegPath = () =>  path.resolve(ffmpegDir, `ffmpeg${ext}`);


export async function getFFMPEGVersion(): Promise<string> {
    return new Promise((res, rej) => {
        child_process.execFile(ffmpegPath(), ['-version'], (error, stdout, stderr) => {
            if (error) {
                return rej(error)
            }
            res(stdout.trim());
        });
    });
}


export async function downloadFFMPEG() {
    const data = await getJSON('https://ffbinaries.com/api/v1/version/latest');
    const url = data.bin[`${platform}-${arch}`]['ffmpeg'];

    if (!url) throw Error('Cannot find a suitable FFMPEG binary for this platform.');

    fs.mkdirSync(ffmpegDir, {recursive: true});

    const response = await axios({
        method: 'get',
        url,
        headers: {
            'accept': 'application/octet-stream',
        },
        responseType: 'stream'
    });

    await new Promise((res, rej) => {
        const pipe = response.data.pipe(unzip.Extract({ path: ffmpegDir }));
        pipe.on('close', res);
        pipe.on('error', rej)
    });

    fs.chmodSync(ffmpegPath(), '755');

    return getFFMPEGVersion();
}


/**
 * Downloads the latest ffmpeg binaries, if they are not currently on the system.
 */
export async function checkFFMPEGDownload(): Promise<string> {
    try {
        return await getFFMPEGVersion();
    } catch (err) {
        return downloadFFMPEG();
    }
}
