import {makeDB} from "./database/db";
import {config, setEnv} from './util/config';


if (config.argCommand) {
    setEnv('./temp-test-data/manual-run/');
    makeDB().then(async () => {
        console.log('Database is ready! Env:', config.shared.env);
        console.log(config.args);
        await config.argCommand!();
    });
}

// TODO: Launch alternate server/UI.
