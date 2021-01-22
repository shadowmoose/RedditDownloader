import axios from 'axios';
import {sharedPath, mkParents} from "../util/paths";
import {downloadBinary} from "../util/http";
import * as fs from "fs";
import path from 'path';
import crypto from 'crypto';
import {ChildProcess} from "child_process";
import {DownloadProgress} from "../util/state";
import {GracefulStopError} from "./downloader";
const ffbinaries = require('ffbinaries');
const YoutubeDlWrap = require("youtube-dl-wrap");

const isWin = process.platform === 'win32' || process.env.NODE_PLATFORM === 'windows';
const ext = isWin ? '.exe':'';
const updateURL = `https://yt-dl.org/downloads/latest/youtube-dl${ext}`;

export const exePath = sharedPath('bin', `ytdl${ext}`);
export const ffmpegDir = sharedPath('bin', 'ffmpeg');

const ffmpegBinary = path.resolve(ffmpegDir, ffbinaries.getBinaryFilename('ffmpeg', ffbinaries.detectPlatform()));
const ytdl = new YoutubeDlWrap(exePath);


export async function getLocalVersion(): Promise<string> {
   try{
       return (await ytdl.getVersion()).trim();
   } catch(err) {
       return '';
   }
}

export async function getLatestVersion() {
    const res = await axios({
        method: 'head',
        url: updateURL,
        maxRedirects: 0
    }).catch(err=>err.response);

    return (res ? res.headers['location']||'':'').match(/\d+\.\d+\.\d+/g)[0];
}


/**
 * Downloads the latest ffmpeg binaries, if they are not currently on the system.
 */
export async function downloadFFMPEG() {
    if (!fs.existsSync(ffmpegBinary)) {
        await new Promise(async res => {
            await mkParents(ffmpegDir);
            ffbinaries.downloadBinaries(['ffmpeg', 'ffprobe'], {destination: ffmpegDir}, () => {
                res();
            });
        });
        ffbinaries.locateBinariesSync(['ffmpeg', 'ffprobe'], {paths: [ffmpegDir], ensureExecutable: true})
    }

    return ffmpegBinary;
}

/**
 * Check the latest local YTDL version, if any, and update if the latest published version doesn't match.
 */
export async function autoUpdate() {
    const loc = await getLocalVersion();
    const rem = await getLatestVersion();

    await downloadFFMPEG();

    if (!loc || rem > loc) {
        await downloadBinary(updateURL, exePath);
        fs.chmodSync(exePath, '755');
        return true;
    }

    return false;
}


function makeArgs(url: string, opts: Record<string, string>) {
    const args = [];

    if(url) args.push(url);

    const all = Object.assign({}, defaultYTOptions, opts);

    for (const k of Object.keys(all)) {
        const v = all[k];

        args.push(k.length === 1 ? `-${k}` : `--${k.replace(/_/gm, '-')}`);
        if (v) args.push(v);
    }

    return args
}


const defaultYTOptions = {
    format: 'bestvideo+bestaudio/best',
    prefer_ffmpeg: '',
    ffmpeg_location: ffmpegBinary,
    add_metadata: '',
    no_playlist: ''
};


/**
 * Downloads a URL using youtube-dl. Returns the full file name, if the download works.
 */
export async function download(url: string, filePath: string, progress?: DownloadProgress): Promise<string> {
    await mkParents(filePath);
    const parDir = path.dirname(filePath);
    const hash = crypto.createHash('md5').update(url).digest('hex').substring(0, 20);
    const tmpPath = path.join(parDir, hash);

    return new Promise(async (res, rej) => {
        // YTDL just randomly ignores extensions, so just let it choose then find it again.
        const download = await ytdl.exec(makeArgs(url,{
            output: tmpPath + '.%(ext)s',
        })).on("progress", (prog: any) => {
            if (progress?.shouldStop) {
                child.kill();
                rej(new GracefulStopError('YTDL Terminated Child'))
            }
            if (progress) {
                progress.status = 'Downloading with YTDL...';
                progress.percent = prog.percent
                progress.knowsPercent = !!prog.percent;
            }
        }).on("error", rej);

        const child: ChildProcess = download.youtubeDlProcess;
        child.on('exit', async function() {
            if (progress?.shouldStop) rej(new GracefulStopError('YTDL Child exit'));
            fs.readdir(parDir, async (err, files) => {
                if(err) rej(err);

                const file = files.find(f => f.includes(hash));
                if (file) {
                    const final = filePath + `${path.extname(file)}`;
                    fs.rename(path.join(parDir, file), final, err => {
                        if (err) rej(err);
                        res(final)
                    });
                } else {
                    rej('No file found matching hash.');
                }
            });
        });
    });
}
