import React, {ReactNode, useEffect, useState} from 'react';
import {observer} from "mobx-react-lite";
import {Button, makeStyles, Modal, Tab, Tabs} from "@material-ui/core";
import IconButton from "@material-ui/core/IconButton";
import SettingsIcon from "@material-ui/icons/Settings";
import {createStyles, Theme} from "@material-ui/core/styles";
import {sendCommand, SETTINGS, useRmdState} from "../../app-util/app-socket";
import {FileHandlingSettingsPanel} from "./file-handling-settings-panel";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import AccountsSettingsPanel from "./accounts-settings-panel";
import {AdvancedConfigPanel} from "./advanced-config-panel";


const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        modalBody: {
            position: 'absolute',
            width: 600,
            height: 450,
            overflowY: 'auto',
            overflowX: 'hidden',
            backgroundColor: theme.palette.background.paper,
            border: '2px solid #000',
            boxShadow: theme.shadows[5],
            padding: theme.spacing(2, 4, 3),
            top: `50%`,
            left: `50%`,
            transform: `translate(-50%, -50%)`,
        },
    }),
);



export const SettingsModal = observer(()=> {
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [oldSettings, setOldSettings] = useState(JSON.stringify(SETTINGS));
    const [currentTab, setCurrentTab] = useState(0);
    const {rmdConnected} = useRmdState();
    const styles = useStyles();
    const canSave = JSON.stringify(SETTINGS) !== oldSettings;

    useEffect(() => {
        snapshotSettings();
    }, [rmdConnected]);

    function snapshotSettings() {
        setOldSettings(JSON.stringify(SETTINGS));
    }

    function openSettings() {
        snapshotSettings();
        setSettingsOpen(true);
    }

    function closeSettings() {
        Object.assign(SETTINGS, JSON.parse(oldSettings));
        setSettingsOpen(false);
    }

    function saveSettings() {
        const old = JSON.parse(oldSettings);
        const current = JSON.parse(JSON.stringify(SETTINGS));

        Promise.all(Object.keys(current).map(k=> {
            if (old[k] !== current[k]) {
                sendCommand(ClientCommandTypes.SAVE_SETTING, {
                    key: k,
                    value: current[k]
                })
            }
        })).then(snapshotSettings);
    }

    return <>
        <IconButton
            color="inherit"
            aria-label="open settings"
            onClick={openSettings}
            edge="start"
        >
            <SettingsIcon />
        </IconButton>

        <Modal
            open={settingsOpen}
            onClose={closeSettings}
        >
            <div className={styles.modalBody}>
                <div style={{marginBottom: '20px'}}>
                    <Tabs
                        value={currentTab}
                        style={{marginBottom: 10}}
                        onChange={(event: React.ChangeEvent<{}>, newValue: number) =>setCurrentTab(newValue)}
                        indicatorColor="primary"
                        textColor="primary"
                        centered
                    >
                        <Tab label="Accounts" />
                        <Tab label="File Handling" />
                        <Tab label="Advanced Config" />
                    </Tabs>

                    <SettingsTabPanel value={currentTab} index={0}>
                        <AccountsSettingsPanel />
                    </SettingsTabPanel>

                    <SettingsTabPanel value={currentTab} index={1}>
                        <FileHandlingSettingsPanel />
                    </SettingsTabPanel>

                    <SettingsTabPanel value={currentTab} index={2}>
                        <AdvancedConfigPanel />
                    </SettingsTabPanel>
                </div>


                <Button
                    disabled={!canSave}
                    variant="contained"
                    color="primary"
                    onClick = {saveSettings}
                    style={{
                        position: 'absolute',
                        bottom: 10
                    }}
                >
                    Save Settings
                </Button>
            </div>
        </Modal>
    </>
});


const SettingsTabPanel = (props: {index: number, value: number, children: ReactNode}) => {
    return <div
        hidden={props.index !== props.value}
    >
        {props.children}
    </div>
}
