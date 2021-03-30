import * as args from '../src/engine/util/arg-parser';
import {ARG_TYPES, ArgCommand, ArgOption, Parser} from '../src/engine/util/arg-parser';


describe('Argument Parser Tests', () => {
    let original = console.log;
    beforeEach(() => {
        console.log = jest.fn();
    });
    afterEach(() => {
        args.setTestingArgv(null);
        console.log = original;
    });

    it("parses complex", async () => {
        args.setTestingArgv([
            'run',
            '-t=this is a=test',
            '--badBool',
            '-Short',
            '1',
            '-boolean'
        ]);
        const opts: ArgOption[] = [
            {
                key: 'boolean',
                type: ARG_TYPES.BOOLEAN,
                description: 'Test Boolean Value.'
            },
            {
                key: 'short',
                type: ARG_TYPES.NUMBER,
                description: 'Short value.'
            },
            {
                key: 'test',
                alts: ['t', 'f'],
                required: true,
                type: ARG_TYPES.STRING,
                description: 'A test option.'
            },
            {
                key: 'missing',
                default: 'default value',
                type: ARG_TYPES.STRING,
            },
            {
                key: 'envVar',
                environment: 'RMD_TEST_USERNAME',
                type: ARG_TYPES.STRING,
                description: 'This is fetched from the environment.'
            }
        ];
        const cmd: ArgCommand = {
            args: opts,
            command: "run",
            helpString: "Run a test",
        }

        const parser = new Parser('Test Argument Parser', 'Parse all the things you want.');
        const res = parser.register(cmd).process();

        if (!res) throw Error('Expected result from parser');

        expect(res).toEqual({
            "args": {
                "boolean": true,
                "envVar": "test_reddit_scraper",
                "missing": "default value",
                "short": 1,
                "test": "this is a=test"
            },
            "command": "run",
            "positional": []
        });
    });

    it('required properties work', () => {
        args.setTestingArgv(['run']);
        const p = new args.Parser('title', 'description');
        const cmd: ArgCommand = {
            args: [
                {
                    key: 't',
                    required: true,
                    type: ARG_TYPES.STRING,
                }
            ],
            command: "run",
            helpString: "Run a test",
            positionalType: ARG_TYPES.NUMBER,
            exampleCalls: ['run --test=1 2 3 4', 'run -t 10']
        }

        p.register(cmd);

        expect(() => p.process(false)).toThrow(); // Fails when missing required.
    })

    it('wrapper parses', () => {
        args.setTestingArgv(['run', '-t', 'test']);
        const p = new args.Parser('title', 'description');
        const cmd: ArgCommand = {
            args: [
                {
                    key: 't',
                    required: true,
                    type: ARG_TYPES.STRING,
                }
            ],
            command: "run",
            helpString: "Run a test",
        }

        p.register(cmd);

        const res = p.process(false);
        expect(res).toEqual({
            "args": {
                "t": "test"
            },
            "command": "run",
            "positional": []
        })
    })

    it('wrapper calls back', () => {
        args.setTestingArgv(['cb', '-t', 'test', '1', '2']);
        const p = new args.Parser('title', 'description');
        const cmd: ArgCommand = {
            args: [
                {
                    key: 't',
                    required: true,
                    type: ARG_TYPES.STRING,
                }
            ],
            command: "cb",
            callback: jest.fn(),
            helpString: "Run a test",
            positionalType: ARG_TYPES.NUMBER
        }

        p.register(cmd);

        p.process(false);
        expect(cmd.callback).toHaveBeenCalledTimes(1);
        expect(cmd.callback).toHaveBeenCalledWith({
            "args": {
                "t": "test"
            },
            "command": "cb",
            "positional": [1, 2]
        });
    })

    it('wrapper prints general help', () => {
        args.setTestingArgv(['-h']);
        const p = new args.Parser('title', 'description');
        const cmd: ArgCommand = {
            args: [
                {
                    key: 't',
                    required: true,
                    type: ARG_TYPES.STRING,
                }
            ],
            command: "cb",
            callback: jest.fn(),
            helpString: "Run a test",
            positionalType: ARG_TYPES.NUMBER
        }

        p.register(cmd);

        p.process(false);
        expect(console.log).toHaveBeenCalled();
        expect(cmd.callback).not.toHaveBeenCalled();
    })

    it('wrapper prints command help', () => {
        args.setTestingArgv(['cb', '-h']);
        const p = new args.Parser('title', 'description');
        const cmd: ArgCommand = {
            args: [
                {
                    key: 't',
                    required: true,
                    type: ARG_TYPES.STRING,
                }
            ],
            command: "cb",
            callback: jest.fn(),
            helpString: "Run a test",
            positionalType: ARG_TYPES.NUMBER
        }

        p.register(cmd);

        p.process(false);
        expect(console.log).toHaveBeenCalled();
        expect(cmd.callback).not.toHaveBeenCalled();
    })
});
