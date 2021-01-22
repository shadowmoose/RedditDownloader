import yargs from "yargs";
import DBSetting from "../database/entities/db-setting";
import * as oa from '../reddit/oAuth';
import {simplePrompt} from "./terminal-util";

export const authConf: yargs.CommandModule = {
    command: 'authorize', // 'authorize <key> [value]'
    aliases: ['auth', 'login'],
    describe: 'Authorize RMD to log into Reddit.',
    builder: {
        refreshToken: {
            description: 'A valid refresh token.',
            alias: ['token'],
            type: 'string'
        }
    },
    handler: async (argv) => {
        return terminalAuthFlow(argv.refreshToken as string)
    }
};

/**
 * Prompts the user to open an oAuth URL, then accepts the redirect URL and saves the refresh code.
 * @param refresh
 */
export async function terminalAuthFlow(refresh?: string) {
    if (refresh) {
        return DBSetting.set('refreshToken', refresh);
    }

    const token = await oa.authFlow(async url => {
        console.log("Please visit this URL:", url);
        console.log('After you accept, you will be redirected to a URL that probably will not load.');
        return await simplePrompt(`Simply copy and paste the URL you are directed to here:`)
    });

    await DBSetting.set('refreshToken', token);
    console.log('Authorized with Reddit!');
}
