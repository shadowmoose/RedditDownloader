import * as qs from 'querystring';
import axios from "axios";


export const port = 7505;
export const state = `${Math.random()}`;  // Exported only for testing.
export const clientID = 'v4XVrdEH_A-ZaA';

const baseURL = 'https://www.reddit.com/api/v1';
const userAgent = `rmd-auth-${Math.random()}`;
const listenerURI = `http://localhost:${port}/authorize`;
const scope: string[] = ['identity', 'read', 'history'];


export function authorizationURL() {
    const params = {
        client_id: clientID,
        response_type: "code",
        state: state,
        redirect_uri: listenerURI,
        duration: 'permanent',
        scope: scope.join(',')
    }
    return `${baseURL}/authorize?${qs.stringify(params)}`;
}

export async function getAccessToken(code: string) {
    const data = {
        grant_type: "authorization_code",
        code: code,
        redirect_uri: listenerURI
    };

    const res = await axios(`${baseURL}/access_token`, {
        data: qs.stringify(data),
        method: 'POST',
        headers: {
            'User-Agent': userAgent
        },
        auth: {
            username: clientID,
            password: ''
        }
    });

    return res.data.refresh_token
}

/**
 * Run through the full auth flow, with a callback that handles opening/prompting the user with the auth URL.
 * @param cb A function, which should return the resulting URL with a `code`.
 */
export async function authFlow(cb: (url: string) => Promise<string>) {
    const url = authorizationURL();

    const auth = await cb(url);
    const params = new URL(auth).searchParams
    const code = params.get('code');

    if (params.get('state') !== state) throw Error('Invalid state passed to auth flow.');
    if (!code) throw Error('No code in the given URL!');

    return getAccessToken(code);
}
