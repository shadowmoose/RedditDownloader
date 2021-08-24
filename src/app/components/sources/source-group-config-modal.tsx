import {observer} from "mobx-react-lite";
import {SourceGroupInterface} from "../../../shared/source-interfaces";
import React, {useMemo, useState} from "react";
import {sendCommand} from "../../app-util/app-socket";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import {Button, Grid, makeStyles, Modal, TextField} from "@material-ui/core";
import {createStyles, Theme} from "@material-ui/core/styles";
import ColorPicker from "material-ui-color-picker";
import {FilterDisplayPanel} from "../filters/filter-display-panel";
import FilterInterface from "../../../shared/filter-interface";


const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        modalBody: {
            position: 'absolute',
            width: 750,
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

export const SourceGroupConfigModal = observer((props: {open: boolean, onClose: (saved: boolean)=>void, sourceGroup: SourceGroupInterface}) => {
    const sg = props.sourceGroup;
    const [saveIDX, setSaveIDX] = useState(0); // Exists simply to track when changes are committed.
    const ogConfigString = useMemo(() => {
        return JSON.stringify(props.sourceGroup);
    }, [props.sourceGroup, saveIDX]);
    const classes = useStyles();
    const needsSave = ogConfigString !== JSON.stringify(sg);
    const hasValidName = !!sg.name.trim();

    function onClose() {
        if (needsSave) {
            const og = JSON.parse(ogConfigString);
            Object.assign(sg, og);
        }
        props.onClose(!needsSave && hasValidName);
    }

    function saveSourceGroup() {
        if (!hasValidName) return;
        const data = JSON.parse(JSON.stringify(sg));
        delete data.sources;
        delete data.filters;

        sendCommand(ClientCommandTypes.UPDATE_OBJECT, {
            dbType: 'DBSourceGroup',
            id: sg.id,
            newValues: data
        }).then(async () => {
            const og: SourceGroupInterface = JSON.parse(ogConfigString);

            // Backfill all Filters. This will update existing, or add new.
            await Promise.all(sg.filters.map(f => {
                return sendCommand(ClientCommandTypes.UPDATE_OBJECT, {
                    dbType: 'DBFilter',
                    id: f.id,
                    newValues: f,
                    parents: [
                        {
                            dbType: 'DBSourceGroup',
                            id: props.sourceGroup.id,
                            property: 'sourceGroup'
                        }
                    ]
                }).then(res => {
                    f.id = res.id;
                });
            }));

            const removedFilters = og.filters.filter(f => !sg.filters.find(sf=>sf.id === f.id));
            await Promise.all(removedFilters.map(f => {
                return sendCommand(ClientCommandTypes.DELETE_OBJECT, {
                    dbType: 'DBFilter',
                    id: f.id
                });
            }));

            setSaveIDX(saveIDX+1);
        });
    }

    function deleteSourceGroup() {
        sendCommand(ClientCommandTypes.DELETE_OBJECT, {
            dbType: 'DBSourceGroup',
            id: sg.id,
        }).then(() => {
            onClose()
        })
    }

    return <Modal
        open={props.open}
        onClose={onClose}
        aria-labelledby="source-group-editor"
        aria-describedby="Edit the selected source group."
    >
        <div className={classes.modalBody}>
            <div style={{flexDirection: 'row'}}>
                <TextField
                    label="Group Name" value={sg.name || ''}
                    onChange={(ev) => {sg.name = ev.target.value}}
                    variant="outlined"
                    error={!hasValidName}
                />
                <ColorPicker
                    name='color'
                    defaultValue={sg.color}
                    value={sg.color}
                    onChange={color => sg.color = color}
                    style={{width: '100px', marginLeft: '20px'}}
                />
            </div>

            <FilterDisplayPanel sourceGroup={sg} />

            <Grid container justify="space-between" >
                <Button
                    disabled={!needsSave || !hasValidName}
                    variant="contained"
                    color="primary"
                    onClick = {saveSourceGroup}
                    style={{marginTop: '20px'}}
                >
                    Save
                </Button>

                <Button
                    variant="contained"
                    color="secondary"
                    onClick = {deleteSourceGroup}
                    style={{marginTop: '20px'}}
                >
                    Delete Group
                </Button>
            </Grid>
        </div>
    </Modal>
});
