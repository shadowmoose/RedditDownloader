import {Box, CircularProgress, Fab, Grid, Popper, Tooltip} from "@material-ui/core";
import CssBaseline from "@material-ui/core/CssBaseline";
import AppBar from "@material-ui/core/AppBar";
import clsx from "clsx";
import Toolbar from "@material-ui/core/Toolbar";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import {SettingsModal} from "./settings-modal/settings-modal";
import Typography from "@material-ui/core/Typography";
import {connectWS, disconnectWS, sendCommand, useRmdState} from "../app-util/app-socket";
import {ClientCommandTypes} from "../../shared/socket-packets";
import GetAppIcon from "@material-ui/icons/GetApp";
import CancelIcon from "@material-ui/icons/Cancel";
import ViewListIcon from "@material-ui/icons/ViewList";
import {RMDStatus} from "../../shared/state-interfaces";
import Drawer from "@material-ui/core/Drawer";
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import Divider from "@material-ui/core/Divider";
import {SourceGroupDrawer} from "./sources/source-group-drawer";
import {StateDropdown} from "./state-display/state-dropdown";
import BasicGallery from "./gallery/basic-gallery/basic-gallery";
import React, {useEffect} from "react";
import {createStyles, makeStyles, Theme} from "@material-ui/core/styles";
import BrowserSettings from "../app-util/local-config";
import {observer} from "mobx-react-lite";
import SettingsBrightnessIcon from '@material-ui/icons/SettingsBrightness';



const drawerWidth = 340;

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        root: {
            display: 'flex',
            backgroundColor: theme.palette.background.default,
            height: '100%'
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
            justifyContent: 'space-between',
        },
        content: {
            flexGrow: 1,
            padding: 10,
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


const AppDisplay = observer(() => {
    const {rmdReady, rmdConnected, rmdState} = useRmdState();
    useEffect(() => {
        connectWS();

        return disconnectWS;
    }, []);

    const classes = useStyles();
    const [open, setOpen] = React.useState(true);
    const [progressAnchorEl, setProgAnchorEl] = React.useState<null | HTMLElement>(null);
    const progBtnRef: any = React.useRef();
    const shouldOpenProgress = !!progressAnchorEl && BrowserSettings.openDownloadProgress;

    const handleDrawerOpen = () => {
        setOpen(true);
    };

    const handleDrawerClose = () => {
        setOpen(false);
    };

    const toggleProgress = () => {
        BrowserSettings.openDownloadProgress = !BrowserSettings.openDownloadProgress;
    };

    const progButtonClass = clsx({
        [classes.progressButtonClosed]: !BrowserSettings.openDownloadProgress,
        [classes.progressButtonOpen]: BrowserSettings.openDownloadProgress,
    });

    useEffect(() => {
        setProgAnchorEl(progBtnRef.current);
    }, [progBtnRef.current]);


    return <Box className={classes.root}>
        <CssBaseline />
        <AppBar
            position="fixed"
            className={clsx(classes.appBar, {
                [classes.appBarShift]: open,
            })}
        >
            <Toolbar>
                <Grid container justifyContent="space-between" >
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
                <IconButton onClick={()=>BrowserSettings.useDarkMode = !BrowserSettings.useDarkMode} >
                    <Tooltip title={'Toggle Dark Mode'}>
                        <SettingsBrightnessIcon />
                    </Tooltip>
                </IconButton>
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
            <div className={classes.drawerHeader} id={'spacerHeader'}/>
            <Popper
                id="progress-popper"
                anchorEl={progressAnchorEl}
                open={shouldOpenProgress}
                className={classes.progressPopover}
            >
                <StateDropdown />
            </Popper>
            <BasicGallery />
        </main>
    </Box>
});

export default AppDisplay;
