import React from 'react';
import {observer} from "mobx-react-lite";
import {TextField, Tooltip, Typography} from "@material-ui/core";
import {SETTINGS} from "../../app-util/app-socket";
import {BoundNumberInput} from "../input-components/number-input";


export const AdvancedConfigPanel = observer(() => {
    return <div>
        <BoundNumberInput
            label={'Concurrent threads'}
            value={SETTINGS.concurrentThreads}
            onUpdate={v => SETTINGS.concurrentThreads = v}
            tooltip={`Maximum number of simultaneous downloads RMD can run. More is generally faster, but uses more system resources.`}
            minimum={1}
        />

        <hr />

        <Tooltip title={`The hostname to bind the server on.`}>
            <TextField
                label="Server hostname"
                variant="outlined"
                style={{width: '100%', marginTop: 20}}
                value={SETTINGS.serverHost}
                onChange={e=>SETTINGS.serverHost = e.target.value.trim()}
            />
        </Tooltip>

        <BoundNumberInput
            label={'Server port'}
            value={SETTINGS.serverPort}
            onUpdate={v => SETTINGS.serverPort = v}
            tooltip={`The port to use for the server.`}
            style={{marginTop: 30}}
            minimum={1000}
        />

        <Typography variant={'caption'} >
            Changes to server values will require a restart to take effect.
        </Typography>
    </div>
});
