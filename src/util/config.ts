/*
    This file synchronously loads the shared configuration data file, as well as any user-provided arguments.
    The `config` export it provides should contain any data required to launch a customized RMD.
 */
import yaml from 'yaml';
import * as path from "path"
import * as fs from "fs";
import envPaths from 'env-paths';
import * as yargs from "yargs";
import {authConf} from "../terminal/authorize";


interface Config {
    /** If set, this is a function that the user invoked via command line. */
    argCommand: Function|null;

    /** The parsed arguments that the user passed in via command line. */
    args: Record<string, any>;

    /** Data saved and loaded from the shared file that all RMD environments use. **/
    shared: {
        /** The most recently used environment path. */
        env: string|null;

        /** A list of all known environments. All are confirmed to currently exist. */
        knownEnvironments: string[]
    }
}

export const config: Config = {
    argCommand: null,
    args: {},
    shared: {
        env: '',
        knownEnvironments: []
    }
};


// ==== PARSE COMMAND-LINE PARAMETERS: ====
const commands = [authConf];
const cmds: yargs.Argv<unknown> = commands.reduce((acc: any, curr: any) => {
    return acc.command({
        ...curr,
        handler: (args: any) => {
            config.argCommand = () => curr.handler(args);
        }
    });
}, yargs);

config.args = cmds.options({
    env: {
        alias: 'e',
        description: 'The directory RMD should create/load.',
        type: 'string'
    },
    sharedDir: {
        description: 'Directory to store shared RMD files.',
        type: 'string'
    }
})
.epilogue('For more information, go to https://github.com/shadowmoose/RedditDownloader')
//.strictOptions()
.env('RMD')
.help()
.argv;


// ==== LOAD SHARED CONFIG FILE: ====

// If we're testing, use a local staged directory:
export const isTest = !!process.env.JEST_WORKER_ID;
const testDir = `./temp-test-data/${Date.now()}-${process.env.JEST_WORKER_ID}/`;
export const CONF_FOLDER = path.resolve(
    isTest? testDir : config.args.sharedDir || envPaths('RedditMediaDownloader', {
        suffix: ''
    }).config
);
const CONF_FILE = path.resolve(CONF_FOLDER, 'rmd-config.yml');

if (!loadShared()) {
    saveShared();
}

checkEnvironment();

/**
 * Set the current environment path we're using. Automatically adds it to known environments, and saves.
 */
export function setEnv(envPath: string) {
    envPath = path.resolve(envPath);
    if (envPath === config.shared.env) return;
    config.shared.env = envPath;
    const known = config.shared.knownEnvironments.filter(e => e!==envPath);
    known.unshift(envPath);
    config.shared.knownEnvironments = known;
    saveShared();
}

/**
 * Saves the current shared configuration state.
 */
function saveShared() {
    fs.mkdirSync(CONF_FOLDER, {recursive: true});
    fs.writeFileSync(CONF_FILE, yaml.stringify(config.shared));
}

/**
 * Loads the current shared configuration state.
 */
function loadShared() {
    if (fs.existsSync(CONF_FILE)) {
        const loaded = yaml.parse(fs.readFileSync(CONF_FILE, 'utf8'));
        Object.assign(config, loaded);
        return true;
    }
    return false;
}


/**
 * Makes sure that the, if set, the current environment exists.
 * If it does not, removes it from the list at tries to load the next known.
 */
function checkEnvironment() {
    const env = config.shared.env;

    config.shared.knownEnvironments = config.shared.knownEnvironments.filter(f => fs.existsSync(f));

    if (env && !fs.existsSync(env)) {
        config.shared.env = null;
    }

    if (!config.shared.env) {
        // Check if we've got any fallback known environments we can use:
        if (config.shared.knownEnvironments.length) {
            setEnv(config.shared.knownEnvironments[0]);
        }
    }

    if (!config.shared.env && isTest) {
        // If testing, dump everything into the same temporary test directory.
        // When run outside of tests, these directories will not be relatives.
        setEnv(path.resolve(testDir, 'downloads')); // TODO: Prompt user on first-time setup.
    }
}
