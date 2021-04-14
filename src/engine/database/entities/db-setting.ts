import {Entity, Column, PrimaryColumn} from 'typeorm';
import {DBEntity} from "./db-entity";
import {defaultSettings, SettingsInterface} from "../../../shared/state-interfaces";


@Entity({ name: 'settings' })
export default class DBSetting extends DBEntity {
    @PrimaryColumn({length: 20})
    id!: string;

    @Column({ type: "text" })
    valueJSON!: string;

    get value () {
        return JSON.parse(this.valueJSON)
    }

    set value (val: any) {
        this.valueJSON = JSON.stringify(val)
    }

    /**
     * Retrieve the value of the given Setting key. Returns the default if none is saved.
     * Once returned from DB, this value is cached in memory. Thus, repeated lookups will not cause slowdown.
     */
    static async get<S extends SettingsInterface, K extends keyof SettingsInterface>(key: K): Promise<S[K]> {
        if (settingsCache[key]) {
            return settingsCache[key];
        }

        const s = await DBSetting.findOne({ id: key as string });
        const def: any = defaultSettings[key];

        return settingsCache[key] = (s ? s.value : def);
    }

    /**
     * Set the value of the given Setting key. Automatically saves. Also updates the in-memory settings cache.
     */
    static async set<S extends SettingsInterface, K extends keyof S>(key: K, val: S[K]): Promise<DBSetting> {
        const found = await DBSetting.findOne({ id: key as string });
        const s = found || await DBSetting.build({id: key as string, valueJSON: ''});
        s.value = val;

        settingsCache[key] = val;

        return s.save();
    }

    /**
     * Retrieves an object with all current setting keys and values.
     * Useful for sending to any interface that needs to know all current settings.
     */
    static async getAll(): Promise<SettingsInterface> {
        const settings = await DBSetting.find();
        const find = (id: string) => settings.find(s => s.id === id);
        const ret: Record<any, any> = {};
        Object.keys(defaultSettings).forEach((key: string) => {
           // @ts-ignore
            ret[key] = find(key)?.value || defaultSettings[key];
        });
        return ret as typeof defaultSettings;
    }
}

const settingsCache: Record<any, any> = {};

if (!!process.env.JEST_WORKER_ID) {
    // If we're testing currently, pre-seed the cache so the DB does not need to initialize for simple setting lookups.
    settingsCache['refreshToken'] = process.env.RMD_REFRESH_TOKEN;
    settingsCache['userAgent'] = `RMD-test-${Math.random()}`;
    settingsCache['imgurClientId'] = process.env.RMD_IMGUR_ID;
}
