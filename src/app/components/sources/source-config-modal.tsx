import {observer} from "mobx-react-lite";
import React, {useMemo, useState} from "react";
import {SourceInterface, SourceTypes} from "../../../shared/source-interfaces";
import {Button, FormControl, Grid, InputLabel, makeStyles, Modal, Select, TextField} from "@material-ui/core";
import {createStyles, Theme} from "@material-ui/core/styles";
import {removeSource, sendCommand} from "../../app-util/app-socket";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import {observable} from "mobx";
import {SavedPostDataForm} from "./source-data-forms/saved-post-data-form";
import Divider from "@material-ui/core/Divider";
import {UpvotedPostDataForm} from "./source-data-forms/upvoted-post-data-form";
import {SubredditPostsDataForm} from "./source-data-forms/subreddit-posts-data-form";


const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        modalBody: {
            position: 'absolute',
            width: 600,
            backgroundColor: theme.palette.background.paper,
            border: '2px solid #000',
            boxShadow: theme.shadows[5],
            padding: theme.spacing(2, 4, 3),
            top: `50%`,
            left: `50%`,
            transform: `translate(-50%, -50%)`,
        },
        formControl: {
            margin: theme.spacing(1),
            minWidth: 120,
        },
    }),
);

function snapshot(obj: any) {
    return JSON.parse(JSON.stringify(obj));
}

export const SourceConfigModal = observer((props: {open: boolean, onClose: (saved: boolean)=>void, source: SourceInterface, sourceGroupID: number}) => {
    const [saveIDX, setSaveIDX] = useState(0); // Exists simply to track when changes are committed.
    const ogConfigString = useMemo(() => {
        return JSON.stringify(props.source);
    }, [props.source, saveIDX]);
    const sourceData = useMemo(() => {
        return observable(JSON.parse(props.source.dataJSON))
    }, [props.source]);
    const source = props.source;
    const classes = useStyles();

    source.dataJSON = JSON.stringify(sourceData);
    const needsSave = ogConfigString !== JSON.stringify(source);
    const hasValidName = !!source.name.trim();

    function onClose() {
        if (needsSave) {
            const og = JSON.parse(ogConfigString);
            Object.assign(source, og);
            console.debug('Reverted unsaved source:', source.id, source.name);
        }
        props.onClose(!needsSave && hasValidName);
    }

    function changeSourceType(e: any) {
        source.type = e.target.value as SourceTypes;
        for (const k of Object.keys(sourceData)) {
            delete sourceData[k];
        }
    }

    function saveSource() {
        if (!hasValidName) return;
        sendCommand(ClientCommandTypes.UPDATE_OBJECT, {
            dbType: 'DBSource',
            id: source.id,
            newValues: snapshot(source),
            parents: [
                {
                    dbType: 'DBSourceGroup',
                    id: props.sourceGroupID,
                    property: 'sourceGroup'
                }
            ]
        }).then(() => {
            setSaveIDX(saveIDX+1);
        });
    }

    function deleteSource() {
        removeSource(props.sourceGroupID, source.id);
        sendCommand(ClientCommandTypes.DELETE_OBJECT, {
            dbType: 'DBSource',
            id: source.id
        }).then(() => {
            onClose();
        });
    }

    return <Modal
        open={props.open}
        onClose={onClose}
        aria-labelledby="source-editor"
        aria-describedby="Edit the selected source."
    >
        <div className={classes.modalBody}>
            <FormControl className={classes.formControl} style={{width: '100%'}}>
                <TextField
                    label="Source Name" value={source.name || ''}
                    onChange={(ev) => {source.name = ev.target.value}}
                    style={{width: '100%'}}
                    variant="outlined"
                    error={!hasValidName}
                />
            </FormControl>
            <FormControl className={classes.formControl} style={{width: '100%'}} variant="filled">
                <InputLabel htmlFor="select-source-type">What should this source download?</InputLabel>
                <Select
                    native
                    defaultValue={source.type}
                    id="select-source-type"
                    onChange={changeSourceType}
                    style={{width: '100%'}}
                >
                    <optgroup label="Reddit">
                        <option value={SourceTypes.UPVOTED_POSTS}>My Upvoted Submissions</option>
                        <option value={SourceTypes.SAVED_POSTS}>My Saved Submissions and Comments</option>
                        <option value={SourceTypes.SUBREDDIT_POSTS}>Submissions in a Subreddit</option>
                    </optgroup>
                    <optgroup label="PushShift">
                        <option value={3}>Option 3</option>
                        <option value={4}>Option 4</option>
                    </optgroup>
                </Select>
            </FormControl>

            {getSourceConfigPage(source.type, sourceData)}
            <Divider style={{marginBottom: '10px', marginTop: '10px'}}/>

            <Grid container justify="space-between" >
                <Button
                    disabled={!needsSave || !hasValidName}
                    variant="contained"
                    color="primary"
                    onClick = {saveSource}
                >
                    Save
                </Button>

                <Button
                    disabled={source.id === undefined || source.id === null}
                    variant="contained"
                    color="secondary"
                    onClick = {deleteSource}
                >
                    Delete Source
                </Button>
            </Grid>
        </div>
    </Modal>
});


/**
 * Using the given source type, return an HTML form which wraps all the available configuration for the Source.
 * @param sourceType
 * @param data
 */
export function getSourceConfigPage(sourceType: SourceTypes, data: any) {
    switch (sourceType) {
        case SourceTypes.SAVED_POSTS:
            return <SavedPostDataForm data={data} />
        case SourceTypes.UPVOTED_POSTS:
            return <UpvotedPostDataForm data={data} />
        case SourceTypes.SUBREDDIT_POSTS:
            return <SubredditPostsDataForm data={data} />
        default:
            return <div>Unknown source: {sourceType}</div>
    }
}
