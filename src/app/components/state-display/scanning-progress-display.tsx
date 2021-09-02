import {observer} from "mobx-react-lite";
import React from "react";
import { STATE } from "../../app-util/app-socket";
import {Grid, Tooltip} from "@material-ui/core";
import SearchIcon from '@material-ui/icons/Search';
import LinkIcon from '@material-ui/icons/Link';
import RedditIcon from '@material-ui/icons/Reddit';
import Typography from "@material-ui/core/Typography";


export const ScanningProgressDisplay = observer(() => {

    return <Grid style={{
        display: 'flex',
        justifyContent: 'space-between'
    }}>
        <Tooltip title={'Total new posts found during this scan.'}>
            <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}>
                <SearchIcon color={'primary'} /> {STATE.newPostsScanned.toLocaleString()}
            </div>
        </Tooltip>

        <Tooltip title={'Remaining downloads in the queue'}>
            <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}>
                <LinkIcon style={{fill: 'green'}}/> {STATE.downloadsInQueue.toLocaleString()}
            </div>
        </Tooltip>

        <Tooltip title={STATE.currentSource ? `Currently scanning source: ${STATE.currentSource}` : 'Finished scanning sources.'}>
            <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}>
                <RedditIcon color={'secondary'} /> <span style={{maxWidth: 150, overflow: 'hidden'}}><Typography noWrap>{STATE.currentSource || 'Done.'}</Typography></span>
            </div>
        </Tooltip>
    </Grid>
});
