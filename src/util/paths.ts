import * as path from "path"
import * as fs from "fs";
import { config, CONF_FOLDER } from './config';


/** Convert a relative path into an absolute path within the current environment data directory. */
export const envDataPath = (...file: string[]) => {
    if (!config.shared.env) throw Error('Cannot build data path - current working environment is not set!');
    return path.resolve(config.shared.env, '.rmd-data', ...file);
}

/** Convert a relative file path into an absolute file path within the current root environment directory. */
export const getAbsoluteDL = (subPath: string) => {
    if (!config.shared.env) throw Error('Cannot get DL Location - current working environment is not set!');
    return path.resolve(config.shared.env, subPath);
}

/** Convert a relative path into an absolute path within the globally-shared config/data directory. */
export const sharedPath = (...file: string[]) => path.resolve(CONF_FOLDER, ...file);

/** Path to the shared static assets directory. Swaps automaticlly between packaged and sourcecode file locations. */
export const assetPath = (...file: string[]) => {
    // @ts-ignore
    if (process.pkg) {
        return path.resolve(__dirname, '../../assets', ...file);
    }
    return path.resolve(__dirname, '../../assets', ...file);
}

/**
 * Build all the parent directories required to make this file valid.
 */
export const mkParents = (file: string) => {
    return new Promise<void>((res, rej) => {
        fs.mkdir(path.dirname(file), { recursive: true }, (err)=>{
            if(err) rej(err);
            res();
        })
    });
}
