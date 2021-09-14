import {AlbumFileDetails, DownloadSearchResult} from "../../../shared/search-interfaces";
import AudiotrackIcon from "@material-ui/icons/Audiotrack";
import Typography from "@material-ui/core/Typography";
import React, {useEffect, useRef, useState} from "react";
import {Grid, makeStyles, Modal, Tooltip} from "@material-ui/core";
import {createStyles, Theme} from "@material-ui/core/styles";
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import RedditIcon from "@material-ui/icons/Reddit";
import LinkIcon from "@material-ui/icons/Link";
import CollectionsIcon from '@material-ui/icons/Collections';
import MovieIcon from '@material-ui/icons/Movie';
import BrowserSettings from "../../app-util/local-config";
import {observer} from "mobx-react-lite";
import {sendCommand} from "../../app-util/app-socket";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import IconButton from "@material-ui/core/IconButton";
import {ArrowBack, ArrowForward} from "@material-ui/icons";


const useStyles = makeStyles((_theme: Theme) =>
    createStyles({
        mediaModalBody: {
            position: 'absolute',
            maxHeight: '90%',
            maxWidth: '90%',
            top: `50%`,
            left: `50%`,
            transform: `translate(-50%, -50%)`,
            outline: 'none',
            display: 'flex',
            justifyContent: 'center',
            flexDirection: 'column',
            alignItems: 'center'
        },
    }),
);


type Dimensions = {
    width: number;
    height: number
}

/**
 * Basic React hook that returns the absolute dimensions (in PX) media should be allowed to take in fullscreen.
 */
function useMediaFitDimensions(): Dimensions {
    function getWindowDimensions() {
        const { innerWidth: width, innerHeight: height } = window;
        return {
            width: Math.floor(width*.9),
            height: Math.floor(height*.8)
        };
    }

    const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

    useEffect(() => {
        function handleResize() {
            setWindowDimensions(getWindowDimensions());
        }

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return windowDimensions;
}


export function MediaWrapper(props: { dl: DownloadSearchResult, maxSize: number}) {
    const [fullScreen, setFullScreen] = useState(false);
    const dimensions = useMediaFitDimensions();
    const classes = useStyles();
    const [index, setIndex] = useState(0);

    const icon = getBestMedia(props.dl, true, {width: props.maxSize, height: props.maxSize});
    const bigVersion = getBestMedia(props.dl, false, dimensions, index, setIndex);

    return <>
        <Modal open={fullScreen} onClose={()=>setFullScreen(false)}>
                <div className={classes.mediaModalBody}>
                    <DisplayHeader dl={props.dl} dimensions={dimensions} />
                    {bigVersion}
                </div>
        </Modal>

        <Tooltip title={`[${props.dl.author}] ${props.dl.title}`}>
            <div
                style={{
                    maxWidth: props.maxSize,
                    maxHeight: props.maxSize,
                    height: 'auto',
                    cursor: 'pointer',
                    position: 'relative'
                }}
                onClick={()=>setFullScreen(true)}
            >
                {icon}
                <DisplayIconBar dl={props.dl} dimensions={dimensions} />
            </div>
        </Tooltip>
    </>
}


function getBestMedia(dl: DownloadSearchResult, thumbnail: boolean, dimensions: Dimensions, index?: number, setIndex?: (idx: number)=>void) {
    const type = dl.albumFiles?.firstFile?.type || dl.type;

    if (dl.isAlbumParent) {
        return <DisplayAlbum dl={dl} thumbnail={thumbnail} dimensions={dimensions} index={index} setIndex={setIndex} />
    }

    switch ((type || '').split('/')[0]) {
        case 'image':
            return <DisplayImage dl={dl} thumbnail={thumbnail} dimensions={dimensions} />
        case 'video':
            return <DisplayVideo dl={dl} thumbnail={thumbnail} dimensions={dimensions} />
        case 'audio':
            return <DisplayAudio dl={dl} thumbnail={thumbnail} dimensions={dimensions} />
        default:
            return <div title={`[${dl.author}] ${dl.title}`} >Cannot Display Media Type "{type}"</div>;
    }
}


const DisplayIconBar = observer((props: { dl: DownloadSearchResult, dimensions: Dimensions}) => {
    return <div
        style={{
            maxWidth: Math.min(100, props.dimensions.width),
            position: 'absolute',
            top: 3,
            left: 3,
            display: 'flex',
            justifyContent: 'space-between',
            background: 'rgba(0,0,0,.7)',
        }}
    >
        {props.dl.isAlbumParent && (props.dl.albumFiles?.count||0) > 1 ? <CollectionsIcon color={'secondary'} /> : null}
        {(!BrowserSettings.autoPlayVideo) && (props.dl.type||'').startsWith('video') ? <MovieIcon color={'secondary'} /> : null}
    </div>
});


function DisplayHeader(props: {dl: DownloadSearchResult, dimensions: Dimensions}) {
    function openURL() {
        window.open('https://redd.it/' + props.dl.submissionId.replace('t3_',''));
    }

    return <div
        style={{
            minWidth: '200px',
            maxWidth: props.dimensions.width
        }}
    >
        <Grid
            style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: "center",
                wordWrap: "break-word",
                maxWidth: Math.max(Math.floor(props.dimensions.width/4), 450),
                minWidth: 450,
                background: 'rgba(0,0,0,.7)',
                padding: 8,
                border: '1px solid black'
            }}
        >
            <div style={{width: 150, marginRight: 10}}>
                <div style={{display: 'flex', flexDirection: 'row', alignItems: "center"}}>
                    <AccountCircleIcon color={'primary'} />
                    <Tooltip title={props.dl.author}>
                        <Typography variant={'caption'} noWrap>
                            {props.dl.author}
                        </Typography>
                    </Tooltip>
                </div>

                <div style={{display: 'flex', flexDirection: 'row', alignItems: "center"}}>
                    <RedditIcon color={'secondary'} />
                    <Tooltip title={props.dl.subreddit}>
                        <Typography variant={'caption'} noWrap>
                            {props.dl.subreddit}
                        </Typography>
                    </Tooltip>
                </div>
            </div>

            <LinkIcon style={{fill: 'green'}}/>
            <Tooltip title={`Open Post: ${props.dl.title}`}>
                <Typography
                    style={{
                        cursor: 'pointer'
                    }}
                    onClick={openURL}
                    variant={'caption'}
                    noWrap
                >
                    {props.dl.title}
                </Typography>
            </Tooltip>
        </Grid>

    </div>
}


function DisplayImage(props: { dl: DownloadSearchResult, thumbnail: boolean, dimensions: Dimensions}) {
    const dl = props.dl;

    return <img
        src={`/file/${dl.id}`}
        alt={`[${dl.author}] ${dl.title}`}
        style={{
            border: '3px solid blue',
            maxWidth: props.dimensions.width,
            maxHeight: props.dimensions.height,
            height: 'auto',
        }}
    />
}


const DisplayVideo = observer((props: { dl: DownloadSearchResult, thumbnail: boolean, dimensions: Dimensions}) => {
    const dl = props.dl;
    const [auto,setAuto] = useState(BrowserSettings.autoPlayVideo);
    const ref = useRef<any>();

    useEffect(() => {
        if (BrowserSettings.autoPlayVideo !== auto) {
            setAuto(BrowserSettings.autoPlayVideo);
            if (ref.current) {
                setTimeout(()=>ref.current[BrowserSettings.autoPlayVideo ? 'play' : 'pause'](), 1);
            }
        }
    }, [BrowserSettings.autoPlayVideo]);

    useEffect(() => {
        if (ref?.current) {
            ref.current.load();
            if (BrowserSettings.autoPlayVideo || !props.thumbnail) {
                ref.current.play().catch((_err: any) => {});
            }
        }
    }, [props.dl.id]);

    // TODO: Look into custom player, maybe, for things like playback speed or sound editing.
    // TODO: Pause when off screen.

    return <video
        ref={ref}
        controls={!props.thumbnail}
        loop={true}
        autoPlay={!props.thumbnail || BrowserSettings.autoPlayVideo}
        muted={props.thumbnail}
        playsInline={props.thumbnail}
        preload={"metadata"}
        style={{
            border: '3px solid green',
            maxWidth: props.dimensions.width,
            maxHeight: props.dimensions.height,
            height: 'auto',
        }}
    >
        <source src={`/file/${dl.id}`} type={dl.type}/>
    </video>
});


function DisplayAudio(props: { dl: DownloadSearchResult, thumbnail: boolean, dimensions: Dimensions}) {
    const dl = props.dl;

    if (props.thumbnail) {
        return <div
            style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                border: '3px solid orange',
            }}
        >
            <div>
                <AudiotrackIcon style={{fontSize: 40}}/>
            </div>
            <div style={{width: props.dimensions.width, wordWrap: "break-word"}}>
                <Typography variant={'subtitle2'} noWrap>{dl.title}</Typography>
            </div>
        </div>
    }

    // Maybe use a better audio player than the built-in one. This is more robust, but fairly ugly.

    return <audio
        controls={!props.thumbnail}
        loop={true}
        autoPlay
        muted={props.thumbnail}
        playsInline={props.thumbnail}
        style={{
            border: '3px solid orange',
            minWidth: '350px',
            minHeight: '60px',
        }}
    >
        <source src={`/file/${dl.id}`} type={dl.type}/>
    </audio>
}


function DisplayAlbum (props: { dl: DownloadSearchResult, thumbnail: boolean, dimensions: Dimensions, index?: number, setIndex?: (n: number)=>any}) {
    const dl: DownloadSearchResult = JSON.parse(JSON.stringify(props.dl));
    const [files, setFiles] = useState<AlbumFileDetails[]>([]);
    const index = props.index || 0;
    const setIndex = props.setIndex || console.log;

    useEffect(() => {
        if (files.length || props.thumbnail || !props.dl.albumFiles?.count) return;

        sendCommand(ClientCommandTypes.GET_ALBUM_FILES, {albumID: dl.albumID}).then((res: AlbumFileDetails[]) => {
            setFiles(res);
        });
    }, [props.thumbnail]);

    useEffect(() => {
        if (props.thumbnail) return;

        function onScroll(ev: any) {
            ev.stopPropagation();

            const inc = (ev.deltaY > 0) ? -1 : 1;
            let ix = (index + inc) % files.length;
            if (ix < 0) ix = files.length - 1;
            setIndex(ix);
        }

        document.addEventListener('wheel', onScroll);

        return () => {
            document.removeEventListener('wheel', onScroll);
        }
    }, [props.thumbnail, setIndex, files, index]);

    const overlayEles: JSX.Element[] = [];

    if (!props.thumbnail) {
        overlayEles.push(<div key={'test-display'}>Album: {index+1}/{props.dl.albumFiles?.count}</div>);
        overlayEles.push(<div
            key={'next-index'}
            style={{
                position: 'absolute',
                right: 0,
                top: '50%',
                transform: 'translate(100%, -50%)',
            }}
        >
            <IconButton color="secondary" aria-label='delete' onClick={() => {
                setIndex((index+1) % files.length)
            }}>
                <ArrowForward />
            </IconButton>
        </div>);

        overlayEles.push(<div
            key={'prev-index'}
            style={{
                position: 'absolute',
                left: 0,
                top: '50%',
                transform: 'translate(-100%, -50%)',
            }}
        >
            <IconButton color="secondary" aria-label='delete' onClick={() => {
                let ix = index-1;
                if (ix < 0) ix = files.length - 1;
                setIndex(ix);
            }}>
                <ArrowBack />
            </IconButton>
        </div>);
    }

    Object.assign(dl, {
        type: files[index]?.mimeType || dl.albumFiles?.firstFile?.type,
        id: files[index]?.id || dl.albumFiles?.firstFile?.id,
        isAlbumParent: false
    });

    const baseEle = getBestMedia(dl, props.thumbnail, props.dimensions);

    return <div style={{position: 'relative'}}>
        {baseEle}
        {props.thumbnail ? null : overlayEles}
    </div>
}
