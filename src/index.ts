process.env.UV_THREADPOOL_SIZE = '20'; // Scale up the available libuv thread pool.
import {makeDB} from "./database/db";
import {config, setEnv} from './util/config';


if (config.argCommand) {
    setEnv('./temp-test-data/manual-run/');
    makeDB().then(async () => {
        console.log('Database is ready! Env:', config.shared.env);
        console.log(config.args);
        await config.argCommand!();
    });
} else {
    console.log("Launching in system tray.");
}

// TODO: Launch alternate server/UI.
