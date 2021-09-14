import {observable, reaction} from "mobx";


/**
 * An observable group of auto-loaded, locally-saved browser config.
 */
const BrowserSettings = observable({
    useDarkMode: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,
    openDownloadProgress: true,
    resultsPerPage: 25,
    autoPlayVideo: true
});

const RMD_KEY = 'localRMDSettings'

const mkKey = (key: string) => `${RMD_KEY}-${key}`;

function save (key: any, value: any) {
    localStorage.setItem(mkKey(key), JSON.stringify(value));
}

function load (key: keyof typeof BrowserSettings): any {
    const raw = localStorage.getItem(mkKey(key)) || JSON.stringify(BrowserSettings[key]);
    return JSON.parse(raw);
}


// Load all local settings.
for (const k of Object.keys(BrowserSettings)) {
    // @ts-ignore
    BrowserSettings[k] = load(k);
}

// Save all local settings, to init them.
for (const [k,v] of Object.entries(BrowserSettings)) {
    save(k, v);
}


for (const k of Object.keys(BrowserSettings)) {
    reaction(
        () => BrowserSettings[k as keyof typeof BrowserSettings],
        (val) => {
            // Watch each key for setting changes, and write the back to local storage.
            save(k, val);
        }
    );
}


window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    console.info('Dark Mode toggled by host OS/Browser.');
    BrowserSettings.useDarkMode = e.matches;
});

export default BrowserSettings;
