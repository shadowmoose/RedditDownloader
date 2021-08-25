import {observer} from "mobx-react-lite";
import React from "react";
import { STATE } from "../../app-util/app-socket";
import {Grid} from "@material-ui/core";


export const ScanningProgressDisplay = observer(() => {

    return <Grid>
        <Grid>
            New Posts Scanned: {STATE.newPostsScanned.toLocaleString()}
        </Grid>
        <Grid>
            Scanning Source: {STATE.currentSource}
        </Grid>
    </Grid>
});
