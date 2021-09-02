import React, {useState} from 'react';
import {observer} from "mobx-react-lite";
import {AUTHED_USERNAME, sendCommand, SETTINGS} from "../../app-util/app-socket";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import {Button, Chip, Grid, makeStyles, Modal, TextField, Tooltip, Typography} from "@material-ui/core";
import VpnKeyIcon from '@material-ui/icons/VpnKey';
import FaceIcon from '@material-ui/icons/Face';
import {createStyles, Theme} from "@material-ui/core/styles";


const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        modalBody: {
            position: 'absolute',
            width: 650,
            height: 350,
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


export default function AccountsSettingsPanel () {
    return <div>
        <RedditOAuthInput />
        <hr style={{marginTop: 30}}/>
        <ImgurApiPanel />
    </div>
}


const RedditOAuthInput = observer(() => {
    const [oAuth, setOAuth] = useState<string|null>(null);
    const [manualCode, setManualCode] = useState<string>('');
    const styles = useStyles();
    const username = AUTHED_USERNAME.get();


    function removeAccount() {
        sendCommand(ClientCommandTypes.SET_OAUTH_CODE, {code: null}).then(() => {
            AUTHED_USERNAME.set(null);
        });
    }

    function manuallySubmit() {
        const code = new URL(manualCode).searchParams.get('code');

        console.log('Manual code:', code);
        if (code) {
            sendCommand(ClientCommandTypes.SET_OAUTH_CODE, {code}).then(user => {
                AUTHED_USERNAME.set(user);
                setOAuth(null);
            });
        }
        setManualCode('');
    }

    async function addAccount() {
        if (username) return;
        const win = SETTINGS.serverPort === 7505 && window.open('');
        const url = await sendCommand(ClientCommandTypes.GET_OAUTH_URL);

        setOAuth(url);

        if (win) {
            win.location.href = url;

            let tracker = setInterval(() => {
                if (username) {
                    win.close();
                    clearTimeout(tracker);
                } else if (win.closed) {
                    clearTimeout(tracker);
                } else {
                    try {
                        const urlParams = new URLSearchParams(win.location.search);
                        const code = urlParams.get('code');
                        if (code) {
                            sendCommand(ClientCommandTypes.SET_OAUTH_CODE, {code}).then(user => {
                                win.close();
                                clearTimeout(tracker);
                                AUTHED_USERNAME.set(user);
                                setOAuth(null);
                            });
                        }
                    } catch (e) {/* While on reddit.com we cannot access the window location cross-origin. Ignore the error. */}
                }
            }, 100);
        }
    }

    return <div>
        <Typography variant={'h5'}>
            Reddit Account (required)
        </Typography>
        <Chip
            icon={username ? <FaceIcon /> :<VpnKeyIcon />}
            label={username || 'Click here to securely authorize Account'}
            clickable
            color={username ? "primary" : 'secondary'}
            onDelete={username ? removeAccount : undefined}
            onClick={addAccount}
            // deleteIcon={<DoneIcon />}
        />

        <Modal open={!!oAuth}>
            <div className={styles.modalBody}>
                <Typography variant="h6">
                    Authorize RMD
                </Typography>
                <Typography variant="body2">
                    An authorization page on Reddit should have opened automatically.
                    Please grant RMD account access there, and this window should close automatically.
                </Typography>
                <hr />

                <Typography variant="subtitle2" gutterBottom>
                    If a new window did not open, or this message is not automatically closing:
                </Typography>
                <ol>
                    <li>
                        <a href={oAuth||''} target={'_blank'} style={{color: 'forestgreen'}}>Manually visit the Reddit authentication page here.</a>
                    </li>
                    <li>Click "Allow" to grant RMD read-only account access.</li>
                    <li>Wait for Reddit to send you to a new (probably blank or error) page.</li>
                    <li>Copy the URL you were redirected to, and paste it below.</li>
                </ol>

                <Grid>
                    <TextField
                        label={"Paste Window URL Here"}
                        variant="outlined"
                        value={manualCode}
                        size={'small'}
                        onChange={(e) => setManualCode(e.target.value)}
                    />
                    <Button
                        disabled={!manualCode.trim()}
                        variant="contained"
                        color="primary"
                        onClick = {manuallySubmit}
                    >
                        Manually Submit
                    </Button>
                </Grid>
            </div>
        </Modal>
    </div>
});


const ImgurApiPanel = observer(() => {

    return <div style={{marginTop: 30}}>
        <Tooltip title={`Some imgur albums (and anything NSFW) are private, and can only be accessed via the official API. Provide a valid client ID to access these images.`}>
            <TextField
                label="imgur client ID (optional)"
                variant="outlined"
                style={{width: '100%'}}
                value={SETTINGS.imgurClientId}
                onChange={e=>SETTINGS.imgurClientId = e.target.value.trim()}
            />
        </Tooltip>
        <Typography variant={'caption'} >
            {/* TODO: Redirect to better visual documentation, since additional steps are required here. */}
            To create an imgur client ID, go to the <a href={"https://api.imgur.com/oauth2/addclient"} target={'_blank'} style={{color: 'forestgreen'}}>imgur API registration page.</a>
        </Typography>
    </div>
});
