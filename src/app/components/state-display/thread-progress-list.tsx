import {observer} from "mobx-react-lite";
import React from "react";
import {
    Avatar, Box,
    CircularProgress,
    CircularProgressProps, List,
    ListItem,
    ListItemAvatar,
    ListItemText, Tooltip
} from "@material-ui/core";
import {DownloaderProgressInterface} from "../../../shared/state-interfaces";
import Typography from "@material-ui/core/Typography";
import {STATE} from "../../app-util/app-socket";


export const ThreadProgressList = observer(() => {
    const eles = STATE.activeDownloads
        .filter(ad => !!ad)
        .sort(ad => ad!.thread)
        .map(ad => <ThreadProgressItem prog={ad} key={ad!.thread} />);

    return <List>
        {eles}
    </List>
});


export const ThreadProgressItem = observer((props: {prog: DownloaderProgressInterface|null}) => {
    const prog = props.prog;

    if (!prog) {
        return null;
    }

    return <ListItem>
        <ListItemAvatar>
            <Avatar>
                {prog.knowsPercent ? <CircularProgressWithLabel value={prog.percent*100} /> : <CircularProgress style={{backgroundColor: '#f1b57d'}}/>}
            </Avatar>
        </ListItemAvatar>
        <Tooltip title={prog.fileName}>
            <ListItemText
                primary={prog.fileName}
                secondary={`[${prog.downloader}] ${prog.status}`}
                style={{
                    whiteSpace: "nowrap",
                }}
            />
        </Tooltip>
    </ListItem>
});


function CircularProgressWithLabel(props: CircularProgressProps & { value: number }) {
    const colors: Record<string, string> = {
        0: '#f5bb57',
        25: '#f5f257',
        50: '#cbf557',
        75: '#67f557',
    };
    let col = colors[0];
    Object.keys(colors).sort().forEach((k) => {
        if (parseInt(k) <= props.value) col = colors[k];
    });

    return (
        <Box position="relative" display="inline-flex">
            <CircularProgress variant="determinate" {...props} style={{backgroundColor: col}}/>
            <Box
                top={0}
                left={0}
                bottom={0}
                right={0}
                position="absolute"
                display="flex"
                alignItems="center"
                justifyContent="center"
            >
                <Typography variant="caption" component="div" color="textSecondary">
                    {`${Math.round(
                        props.value,
                    )}%`
                    }</Typography>
            </Box>
        </Box>
    );
}
