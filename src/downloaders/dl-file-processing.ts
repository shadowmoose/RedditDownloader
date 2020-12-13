import crypto from "crypto";
import fs from "fs";
import DBFile from "../database/entities/db-file";
import * as mimetype from "mime-types";
const dHash = require('dhash-image');


export async function distHash(file: string): Promise<string|null> {
    return dHash(file, 8).then(async (res: Buffer) => {
        return res.toString('hex');
    }).catch(() => null);
}


function checksumFile(path: string, hashName = 'sha256'): Promise<string> {
    return new Promise((resolve, reject) => {
        const hash = crypto.createHash(hashName);
        const stream = fs.createReadStream(path);
        stream.on('error', err => reject(err));
        stream.on('data', chunk => hash.update(chunk));
        stream.on('end', () => resolve(hash.digest('hex')));
    });
}


export function hammingDist(str1: string, str2: string) {
    let diff = 0;
    for (let idx = 0; idx < str1.length; idx ++) {
        if (str1[idx] !== str2[idx]) diff++;
    }
    return diff;
}


/**
 * Creates & Saves a DBFile for the given path.
 *
 * Uses hashing to deduplicate files. If a pre-existing match is found,
 * it deletes the worst file and returns the updated File with the new best path.
 */
export async function buildFile(fullPath: string, subpath: string) {
    const stats = await fs.promises.stat(fullPath);
    if (!stats.isFile()) throw Error(`The given file output path does not exist: "${fullPath}"`);

    const checksum = await checksumFile(fullPath);
    const dh = await distHash(fullPath);
    const dChunks = dh?.match(/.{1,4}/g) || [];

    const closeMatches = await DBFile.createQueryBuilder('f')
        .select()
        .where({shaHash: checksum})
        .orWhere('f.hash1 = :hash1', {hash1: dChunks[0]})
        .orWhere('f.hash2 = :hash2', {hash2: dChunks[0]})
        .orWhere('f.hash3 = :hash3', {hash3: dChunks[0]})
        .orWhere('f.hash4 = :hash4', {hash4: dChunks[0]})
        .getMany();
    const match = closeMatches.find(m =>
        checksum === m.shaHash ||
        (m.dHash && dh && hammingDist(m.dHash||'', dh||'') < 4)
    );

    if (match) {
        let best, worst;
        if (match.size > stats.size) {
            best = match.path;
            worst = fullPath;
        } else {
            best = fullPath;
            worst = match.path;
        }

        match.path = best;
        await match.save();
        await fs.promises.unlink(worst);

        return match;
    }

    const res = DBFile.build({
        shaHash: checksum,
        dHash: dh,
        hash1: dChunks[0],
        hash2: dChunks[1],
        hash3: dChunks[2],
        hash4: dChunks[3],
        mimeType: mimetype.lookup(fullPath) || '',
        path: subpath,
        size: stats.size
    });

    return res.save();
}
