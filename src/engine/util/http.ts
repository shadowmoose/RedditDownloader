import fs from "fs";
import axios, {AxiosRequestConfig} from "axios";
import {mkParents} from "./paths";


export async function downloadBinary (url: string, filePath: string) {
    await mkParents(filePath);

    const writer = fs.createWriteStream(filePath);
    const response = await axios({
        url,
        method: 'GET',
        responseType: 'stream',
        timeout: 10000
    });

    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
        writer.on('finish', resolve)
        writer.on('error', reject)
    })
}


export async function getJSON (url: string|URL, headers: Record<string, string> = {}, ext: Partial<AxiosRequestConfig> = {}) {
    if (url instanceof URL) url = url.toString();

    const response = await axios({
        url,
        method: 'GET',
        timeout: 10000,
        headers,
        ...ext
    });

    return response.data;
}
