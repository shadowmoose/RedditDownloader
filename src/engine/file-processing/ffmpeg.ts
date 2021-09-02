import {getJSON} from "../util/http";
import * as child_process from 'child_process';
import {sharedPath} from "../core/paths";
import path from 'path';
import * as os from "os";
import axios from "axios";
import fs from 'fs';
import {ParsedMediaMetadata} from "../../shared/search-interfaces";

const unzip = require('unzip-stream');

const isWin = process.platform === 'win32' || process.env.NODE_PLATFORM === 'windows';
const platform = isWin ? 'windows' : process.platform === 'darwin' ? 'osx' : 'linux';
const arch = os.arch().replace('x', '');
const ext = isWin ? '.exe':'';
export const ffmpegDir = sharedPath('bin', 'ffmpeg');
export const ffmpegPath = () =>  path.resolve(ffmpegDir, `ffmpeg${ext}`);
export const ffprobePath = () =>  path.resolve(ffmpegDir, `ffprobe${ext}`);


export async function getFFMPEGVersion(): Promise<string> {
    return new Promise((res, rej) => {
        child_process.execFile(ffmpegPath(), ['-version'], (error, stdout, _stderr) => {
            if (error) {
                return rej(error)
            }
            res(stdout.trim());
        });
    });
}

export async function getFFProbeVersion(): Promise<string> {
    return new Promise((res, rej) => {
        child_process.execFile(ffprobePath(), ['-version'], (error, stdout, _stderr) => {
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

export async function downloadFFProbe() {
    const data = await getJSON('https://ffbinaries.com/api/v1/version/latest');
    const url = data.bin[`${platform}-${arch}`]['ffprobe'];

    if (!url) throw Error('Cannot find a suitable FFProbe binary for this platform.');

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

    fs.chmodSync(ffprobePath(), '755');

    return getFFProbeVersion();
}


export async function getMediaStreams(path: string): Promise<FFProbeStreamResult> {
    return new Promise((res, rej) => {
        child_process.execFile(ffprobePath(), ['-v', 'error', '-show_entries', 'stream=codec_type,codec_name,duration,width,height,bit_rate', '-show_format', '-print_format', 'json', path], (error, stdout, _stderr) => {
            if (error) {
                return rej(error)
            }
            res((JSON.parse(stdout.trim()) as FFProbeStreamResult));
        });
    });
}

export async function getMediaMetadata(path: string) {
    const meta = await getMediaStreams(path);
    const ret: ParsedMediaMetadata = {
        duration: parseFloat(meta.format.duration) || null,
        bitrate: parseFloat(meta.format.bit_rate) || null,
        width: null,
        height: null,
        videoCodec: null,
        audioCodec: null,
        originalMediaTitle: meta.format.tags?.title || null
    };

    meta.streams.forEach(st => {
        switch (st.codec_type.toLowerCase()) {
            case 'video':
                ret.width = st.width || null;
                ret.height = st.height || null;
                ret.videoCodec = st.codec_name || 'unknown';
                break;
            case 'audio':
                ret.audioCodec = st.codec_name || 'unknown';
                break;
        }
    });

    return ret;
}

export async function fileHasAudio(path: string) {
    try{
        const {streams} = await getMediaStreams(path);
        return streams.some(s => s.codec_type === 'audio');
    } catch (err) {
        return false;
    }
}


/**
 * Downloads the latest ffmpeg binaries, if they are not currently on the system.
 */
export async function checkFFMPEGDownload(): Promise<string> {
    try {
        await getFFProbeVersion();
    } catch (err) {
        await downloadFFProbe();
    }
    try {
        return await getFFMPEGVersion();
    } catch (err) {
        return downloadFFMPEG();
    }
}


interface FFProbeStreamResult {
    streams: [
        {
            "codec_name": string,
            "codec_type": string,
            "width"?: number,
            "height"?: number,
            "duration": string,
            "bit_rate": string
        }
    ],
    format: {
        "filename": string,
        "nb_streams": number,
        "format_name": string,
        "duration": string,
        "size": string,
        "bit_rate": string,
        "probe_score": number,
        "tags"?: {
            "title"?: string,
        }
    }
}

