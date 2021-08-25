import {printTable} from "./output-formatting";

export enum ARG_TYPES {
    BOOLEAN='bool',
    STRING='string',
    NUMBER='number'
}

export interface ArgOption {
    key: string;
    alts?: string[];
    type: ARG_TYPES;
    default?: any;
    required?: boolean;
    environment?: string;
    description?: string;
}

export interface ParsedArgs {
    /** If one was found, returns the command from the args. */
    command: string;
    /** Any additonal positional arguments. */
    positional: any[];
    /** All the converted key->value args that were searched for. */
    args: Record<string, any>;
}

export interface ArgCommand {
    /** The name of this command string. */
    command: string;
    /** The help string to use. */
    helpString: string;
    /** The arguments to parse. */
    args: ArgOption[];
    /** If provided, passes the located arguments into this callback synchronously. */
    callback?: (args: ParsedArgs) => ParsedArgs|void;
    /** If provided, casts all positional args into this type. */
    positionalType?: ARG_TYPES;
    /** A demo call command, to display during help. */
    exampleCalls?: string[];
}


let overwriteArgs: string[]|null = null;
/** Simple method to simulate process args, without actually changing anything process-wide. */
export const setTestingArgv = (args: string[]|null) => overwriteArgs = args? ['', '', ...args] : null;

/**
 * Breaks down the process arguments (or the given argument string) into a generic key/value store format.
 * Normalizes all values to lower case, and strips any hyphens.
 */
export function processArgs() {
    let args: string[] = [];

    (overwriteArgs || process.argv).slice(2).forEach(a => {
        const sp: string[] = [];
        if (a.startsWith('-') && a.includes('=')) {
            const idx = a.indexOf('=');
            sp.push(a.substring(0, idx));
            sp.push(a.substring(idx + 1));
        } else {
            sp.push(a);
        }
        for (const arg of sp) {
            if (!arg.trim()) continue;
            args.push(arg);
        }
    });

    args = args.filter(a => a);

    const parsed: Record<string, any> = {};
    const commands: string[] = [];
    let key: string | null = null;

    for (const a of args) {
        if (a.startsWith('-')) {
            if (key) {
                parsed[key] = 'true';
            }
            key = a.replace(/^-+/, '').toLowerCase();
        } else if (key) {
            parsed[key] = a;
            key = null;
        } else {
            commands.push(a);
        }
    }

    if (key) {
        parsed[key] = 'true';
    }

    return {
        parsed,
        commands
    };
}


/**
 * Search for each of the given ArgOptions in the process args.
 * @param opts
 */
export function parse(opts: ArgOption[]): ParsedArgs {
    const {parsed, commands} = processArgs();
    const ret: Record<string, any> = {};

    for (const opt of opts) {
        const keys = [opt.key, ...(opt.alts ? opt.alts : [])].map(k => k.replace(/^-+/, '').toLowerCase()).filter(k=>k.trim());
        for (const k of keys) {
            if (!parsed.hasOwnProperty(k)) continue;
            ret[opt.key] = convert(parsed[k], opt.type);
        }

        if (!ret.hasOwnProperty(opt.key)) {
            if (opt.environment && process.env.hasOwnProperty(opt.environment)) ret[opt.key] = convert(process.env[opt.environment]!, opt.type);
            if (opt.default !== undefined) ret[opt.key] = opt.default;
        }
    }

    return {
        command: commands[0],
        positional: commands.slice(1),
        args: ret
    };
}


export function convert(val: string, type: ARG_TYPES) {
    switch (type) {
        case ARG_TYPES.STRING:
            return val;
        case ARG_TYPES.BOOLEAN:
            return val.toLowerCase().startsWith('t') || val.toLowerCase().startsWith('y') || val === '1';
        case ARG_TYPES.NUMBER:
            return parseFloat(val);
    }
}



export class Parser {
    private commands: ArgCommand[] = [];
    private readonly title: string;
    private readonly description: string;
    private static HELP_ARG = {
        key: 'help',
        alts: ['h'],
        type: ARG_TYPES.BOOLEAN
    };

    constructor(title: string, description = '') {
        this.title = title;
        this.description = description;
    }

    /**
     * Register a new command to search for, once {@link process} is called.
     * @param command
     */
    register(command: ArgCommand) {
        this.commands.push(command);
        return this;
    }

    /**
     * Parse the command line, looking for any registered commands.
     * If none are found, prints the help message and returns void.
     */
    process(exitOnFail = true): ParsedArgs|void {
        for (const c of this.commands) {
            const res = parse([...c.args, Parser.HELP_ARG]);

            if (res.command === c.command) {
                this.checkRequired(c, res, exitOnFail);
                if (res.args.help) {
                    this.printCommandHelp(c);
                    return;
                }
                if (c.positionalType && res.positional) {
                    res.positional = res.positional.map(p => convert(p, c.positionalType!));
                }
                return c.callback ? c.callback(res) : res;
            }
        }
        this.printCommandSummary();
        return;
    }

    private checkRequired(cmd: ArgCommand, parsed: ParsedArgs, exitOnFail: boolean) {
        if (parsed.args.help) return;
        for (const a of cmd.args) {
            if (a.required && ! parsed.args[a.key]) {
                if (exitOnFail) {
                    console.error('Missing required argument:', a.key);
                    console.error(`Use "${cmd.command} --help" for more info.`);
                    process.exit(1);
                } else {
                    throw Error(`Missing required argument: ${a.key}`);
                }
            }
        }
    }

    /**
     * Display a summary of all commands available.
     */
    printCommandSummary() {
        const mLen = Math.max(this.title.length+4, this.description.length);
        const bef = Math.floor((mLen-this.title.length)/2);
        console.log(`\n${''.padStart(bef, ' ')}${this.title}`);
        console.log(this.description, '\n');

        const cmds = this.commands.map(c => {
            return {
                command: `${c.command}:`,
                desc: c.helpString
            }
        })
        console.log("Available Commands:")
        printTable(cmds, true);
        console.log('For more info: [command] --help\n\n');
        return this;
    }

    /**
     * Print the help box for a Command, and all its inputs.
     * @param cmd
     */
    printCommandHelp(cmd: ArgCommand) {
        console.log(`\n${cmd.command}`, '->', cmd.helpString);
        const output: {argument: any, alts: any, type: any, description: any}[] = [];

        cmd.args.sort((a, b) => (b.required?1:0) - (a.required?1:0)).forEach(a => {
            output.push({
                argument: `-${a.key}${(a.required && a.type !== ARG_TYPES.BOOLEAN) ? '*' : ''}`,
                alts: a.alts,
                type: `[${a.type}]`,
                description: a.description
            })
        });

        if (cmd.positionalType) {
            output.push({
                argument: '...args',
                alts: '',
                type: `[${cmd.positionalType}]`,
                description: '<positional>'
            })
        }

        printTable(output);

        console.log('An \'*\' indicates required arguments.');

        if (cmd.exampleCalls) {
            console.log(`\nEG: ${cmd.exampleCalls.map(c => `"${c}"`).join('\n    ')}`);
        }
        console.log('\n')
        return this;
    }
}

