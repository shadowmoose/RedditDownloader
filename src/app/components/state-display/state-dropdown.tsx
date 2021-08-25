import React from "react";
import {ScanningProgressDisplay} from "./scanning-progress-display";
import {Paper} from "@material-ui/core";
import {ThreadProgressList} from "./thread-progress-list";

const BOUND_WIDTH = 450;

export const StateDropdown = (props: {}) => {

    return <Paper elevation={3} style={{
        width: `${BOUND_WIDTH}px`,
        maxHeight: '400px',
        overflowX: 'hidden',
        overflowY: 'auto',
        padding: '10px',
        margin: '10px'
    }}>
        <ScanningProgressDisplay />
        <ThreadProgressList />
    </Paper>
}
