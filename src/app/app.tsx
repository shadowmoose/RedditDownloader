import React, {useEffect} from 'react';
import {
    connectWS,
    disconnectWS,
    GLOBAL_SERVER_ERROR,
    sendCommand,
    STATE,
    useRmdState
} from "./app-util/app-socket";
import {observer} from "mobx-react-lite";
import {configure} from "mobx";
import clsx from 'clsx';
import {createStyles, makeStyles, Theme} from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ViewListIcon from '@material-ui/icons/ViewList';
import GetAppIcon from '@material-ui/icons/GetApp';
import CancelIcon from '@material-ui/icons/Cancel';
import {CircularProgress, Fab, Grid, Popper, Tooltip} from "@material-ui/core";
import {SourceGroupDrawer} from "./components/sources/source-group-drawer";
import {ClientCommandTypes} from "../shared/socket-packets";
import {RMDStatus} from "../shared/state-interfaces";
import {StateDropdown} from "./components/state-display/state-dropdown";
import {SettingsModal} from "./components/settings-modal/settings-modal";
import {SnackbarProvider, useSnackbar} from "notistack";


configure({
    enforceActions: "never",
});

const drawerWidth = 340;

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        root: {
            display: 'flex',
        },
        appBar: {
            transition: theme.transitions.create(['margin', 'width'], {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
            }),
        },
        appBarShift: {
            width: `calc(100% - ${drawerWidth}px)`,
            marginLeft: drawerWidth,
            transition: theme.transitions.create(['margin', 'width'], {
                easing: theme.transitions.easing.easeOut,
                duration: theme.transitions.duration.enteringScreen,
            }),
        },
        menuButton: {
            marginRight: theme.spacing(2),
        },
        hide: {
            display: 'none',
        },
        drawer: {
            width: drawerWidth,
            flexShrink: 0,
        },
        drawerPaper: {
            width: drawerWidth,
            overflowX: 'hidden',
            overflowY: 'auto'
        },
        drawerHeader: {
            display: 'flex',
            alignItems: 'center',
            padding: theme.spacing(0, 1),
            // necessary for content to be below app bar
            ...theme.mixins.toolbar,
            justifyContent: 'flex-end',
        },
        content: {
            flexGrow: 1,
            padding: theme.spacing(3),
            transition: theme.transitions.create('margin', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
            }),
            marginLeft: -drawerWidth,
        },
        contentShift: {
            transition: theme.transitions.create('margin', {
                easing: theme.transitions.easing.easeOut,
                duration: theme.transitions.duration.enteringScreen,
            }),
            marginLeft: 0,
        },
        progressPopover: {
            display: 'flex',
            alignItems: 'center',
            padding: theme.spacing(0, 1),
            // necessary for content to be below app bar
            ...theme.mixins.toolbar,
            justifyContent: 'flex-end',
        },
        progressButtonWrapper: {
            marginLeft: theme.spacing(1),
            position: 'relative',
            display: 'inline-block'
        },
        progressButtonClosed: {
            width: 48,
            height: 48,
            backgroundColor: '#5fa9dc',
            '&:hover': {
                backgroundColor: '#4e84ac',
            },
        },
        progressButtonOpen: {
            width: 48,
            height: 48,
            backgroundColor: '#4e84ac',
            '&:hover': {
                backgroundColor: '#5fa9dc',
            },
        },
        fabProgress: {
            color: 'rgb(68,236,61)',
            position: 'absolute',
            top: -6,
            left: -6,
            zIndex: 1,
            pointerEvents: 'none'
        },
    }),
);


const App = () => {
    const {rmdReady, rmdConnected, rmdState} = useRmdState();
    useEffect(() => {
        connectWS();

        return disconnectWS;
    }, []);

    const classes = useStyles();
    const [open, setOpen] = React.useState(true);
    const progBtnRef: any = React.useRef();
    const [progressAnchorEl, setProgAnchorEl] = React.useState<null | HTMLElement>(null);

    const handleDrawerOpen = () => {
        setOpen(true);
    };

    const handleDrawerClose = () => {
        setOpen(false);
    };

    const toggleProgress = () => {
        setProgAnchorEl(progressAnchorEl ? null : progBtnRef.current);
    };

    const progButtonClass = clsx({
        [classes.progressButtonClosed]: !progressAnchorEl,
        [classes.progressButtonOpen]: !!progressAnchorEl,
    });

    return (
        <SnackbarProvider maxSnack={5}>
            <div className={classes.root}>
                <CssBaseline />
                <AppBar
                    position="fixed"
                    className={clsx(classes.appBar, {
                        [classes.appBarShift]: open,
                    })}
                >
                    <Toolbar>
                        <Grid container justify="space-between" >
                            <Grid>
                                <IconButton
                                    color="inherit"
                                    aria-label="open drawer"
                                    onClick={handleDrawerOpen}
                                    edge="start"
                                    className={clsx(classes.menuButton, open && classes.hide)}
                                >
                                    <MenuIcon />
                                </IconButton>
                                <SettingsModal />
                            </Grid>

                            <Typography variant="h4" noWrap>
                                Reddit Media Downloader
                            </Typography>

                            <Grid>
                                <Fab
                                    variant="extended"
                                    disabled={!rmdConnected}
                                    color={rmdReady ? 'default' : 'secondary'}
                                    onClick={() => {
                                        sendCommand(rmdReady ? ClientCommandTypes.START_DOWNLOAD : ClientCommandTypes.STOP_DOWNLOAD, {})
                                    }}
                                >
                                    {rmdReady ? <GetAppIcon /> : <CancelIcon />}
                                    <span style={{marginLeft: '5px'}}>
                                    {rmdReady ? 'Start Download' : 'Stop Downloading'}
                                </span>
                                </Fab>

                                <div className={classes.progressButtonWrapper}>
                                    <Tooltip title="Toggle Details">
                                        <Fab
                                            aria-label="save"
                                            color="primary"
                                            onClick={toggleProgress}
                                            className={progButtonClass}
                                            ref={progBtnRef}
                                        >
                                            <ViewListIcon />
                                        </Fab>
                                    </Tooltip>
                                    {rmdState === RMDStatus.RUNNING && <CircularProgress size={60} className={classes.fabProgress} /> }
                                </div>
                            </Grid>
                        </Grid>
                    </Toolbar>
                </AppBar>


                <Drawer
                    className={classes.drawer}
                    variant="persistent"
                    anchor="left"
                    open={open}
                    classes={{
                        paper: classes.drawerPaper,
                    }}
                >
                    <div className={classes.drawerHeader}>
                        <IconButton onClick={handleDrawerClose}>
                            <ChevronLeftIcon />
                        </IconButton>
                    </div>
                    <Divider />
                    <SourceGroupDrawer />
                </Drawer>


                <main
                    className={clsx(classes.content, {
                        [classes.contentShift]: open,
                    })}
                >
                    <div className={classes.drawerHeader} />
                    <Popper
                        id="progress-popper"
                        anchorEl={progressAnchorEl}
                        open={!!progressAnchorEl}
                        className={classes.progressPopover}
                    >
                        <StateDropdown />
                    </Popper>
                    <StateDebug />
                </main>
            </div>
            <NotifyComponent />
        </SnackbarProvider>
    );
};


const StateDebug = observer(() => {
    return <div>
        <pre>
            {JSON.stringify(STATE, null, 4)}
        </pre>
    </div>
});


/**
 * Handles listening for notifications, while existing within the DOM for access to the Snackbar component.
 */
const NotifyComponent = observer(() => {
    const { enqueueSnackbar } = useSnackbar();
    const alert = GLOBAL_SERVER_ERROR.get();

    useEffect(() => {
        if (!alert) return;
        const {message, options} = JSON.parse(alert);
        enqueueSnackbar(message, options);
    }, [alert]);

    return <></>
});

export default App;
