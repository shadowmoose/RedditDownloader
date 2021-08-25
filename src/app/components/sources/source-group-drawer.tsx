import React, {useState} from 'react';
import {observer} from "mobx-react-lite";
import {sendCommand, SOURCE_GROUPS} from "../../app-util/app-socket";
import Typography from "@material-ui/core/Typography";
import {
    DragDropContext,
    Draggable,
    DraggableProvided,
    DraggableStateSnapshot,
    Droppable,
    DropResult
} from "react-beautiful-dnd";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Button,
    Fade,
    Grid,
    IconButton, makeStyles, Modal, TextField,
    Tooltip
} from "@material-ui/core";
import SettingsIcon from '@material-ui/icons/Settings';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import DragIndicatorIcon from '@material-ui/icons/DragIndicator';
import {SourceGroupInterface, SourceInterface, SourceTypes} from "../../../shared/source-interfaces";
import {SourceConfigModal} from "./source-config-modal";
import {SourceGroupConfigModal} from "./source-group-config-modal";
import {createStyles, Theme} from "@material-ui/core/styles";
import ColorPicker from "material-ui-color-picker";



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
        }
    }),
);


export const SourceGroupDrawer = observer(() => {
    const [creatingNew, setCreating] = useState(false);
    const eles = SOURCE_GROUPS.map(sg => {
        return <SourceGroupEle key={sg.id} sourceGroup={sg} />
    });

    function onDragEnd(result: DropResult) {
        const { source, destination } = result;
        if (!destination) return;

        const targetSG = SOURCE_GROUPS.find(sg => sg.id === parseInt(destination.droppableId));
        const ogSG = SOURCE_GROUPS.find(sg => sg.id === parseInt(source.droppableId));
        if (!targetSG || !ogSG) throw Error(`Unknown source group ID: ${destination.droppableId}!`);

        const [movingSource] = ogSG.sources.splice(source.index, 1);
        targetSG.sources.splice(destination.index, 0, movingSource);

        if (destination.droppableId !== source.droppableId) {
            // Send update to server.
            sendCommand(ClientCommandTypes.UPDATE_OBJECT, {
                dbType: 'DBSource',
                id: movingSource.id,
                newValues: {},
                parents: [
                    {
                        dbType: 'DBSourceGroup',
                        id: targetSG.id,
                        property: 'sourceGroup'
                    }
                ]
            })
        }
    }

    return <DragDropContext onDragEnd={onDragEnd}>
        {eles}

        <Grid container justify="center">
            <Button
                variant="outlined"
                color={"primary"}
                style={{marginTop: '10px', marginBottom: '4px'}}
                onClick={()=>setCreating(true)}
            >
                Add new Source Group.
            </Button>
        </Grid>

        <CreateSourceGroupModal open={creatingNew} onClose={()=>setCreating(false)}/>
    </DragDropContext>
});


/**
 * Modal for creating a new Source Group.
 */
export const CreateSourceGroupModal = (props: {open: boolean, onClose: any}) => {
    const pastelHex = () => {
        let R = Math.floor((Math.random() * 127) + 127);
        let G = Math.floor((Math.random() * 127) + 127);
        let B = Math.floor((Math.random() * 127) + 127);

        let rgb = (R << 16) + (G << 8) + B;
        return `#${rgb.toString(16)}`;
    }
    const classes = useStyles();
    const [name, setName] = useState('');
    const [color, setColor] = useState(pastelHex);
    const nameError = !name.trim().length;

    function createSourceGroup() {
        const sg: Partial<SourceGroupInterface> = {
            color,
            name,
            filters: [],
            sources: []
        };

        sendCommand(ClientCommandTypes.UPDATE_OBJECT, {
            dbType: 'DBSourceGroup',
            newValues: sg
        }).then(res => {
            props.onClose();
            sg.id = res.id;
            SOURCE_GROUPS.push(sg as SourceGroupInterface);
            setName('');
            setColor(pastelHex());
        });
    }

    return <Modal
        open={props.open}
        onClose={props.onClose}
        aria-labelledby="source-group-creator"
        aria-describedby="Create a new source group."
    >
        <div className={classes.modalBody}>
            <Typography variant="h5" noWrap>
                Create a Group for Sources
            </Typography>

            <TextField
                label="Group Name" value={name}
                onChange={(ev) => {setName(ev.target.value)}}
                style={{width: '100%'}}
                variant="outlined"
                error={nameError}
            />

            <Grid>
                <Typography variant="h6" noWrap style={{display: 'inline'}}>
                    Color:
                </Typography>
                <ColorPicker
                    name='color'
                    defaultValue={color}
                    value={color}
                    onChange={setColor}
                    style={{width: '100px', marginLeft: '20px'}}
                />
            </Grid>

            <Button
                disabled={nameError}
                variant="contained"
                color="primary"
                onClick = {createSourceGroup}
                style={{marginTop: '20px'}}
            >
                Save
            </Button>
        </div>
    </Modal>
}



export const SourceGroupEle = observer((props: {sourceGroup: SourceGroupInterface}) => {
    const sg = props.sourceGroup;
    const [newSource, setNewSource] = useState<SourceInterface|null>(null);
    const [edit, setEdit] = useState(false);

    const sources = sg.sources.map((s: any, idx: number) => {
        return <SourceDraggableEle source={s} key={s.id} idx={idx} sourceGroupID={sg.id} />
    });

    const getListStyle = (isDraggingOver: boolean) => ({
        background: isDraggingOver ? "rgba(0,0,0,.2)" : ''
    });

    function addNewSource() {
        const s = createNewSource();
        console.log('Creating:', s);
        sg.sources.push(s); // Append, then find the observable.
        setNewSource(sg.sources.find(src=>src.id === s.id) as SourceInterface);
    }

    function onEditorClose(saved: boolean) {
        if (newSource && !saved) {
            console.log('Cancelled new source!');
            const idx = sg.sources.findIndex(s=>s.id === newSource.id);
            if (idx >= 0) {
                sg.sources.splice(sg.sources.findIndex(s=>s.id === newSource.id), 1);
            }
        }
        setNewSource(null);
    }

    return <>
        <Accordion
            className={'SourceGroupEle'}
            TransitionProps={{ unmountOnExit: true }}
            defaultExpanded={true}
            style={{background: sg.color}}
        >
            {newSource && <SourceConfigModal open={!!newSource} onClose={onEditorClose} source={newSource} sourceGroupID={sg.id} />}
            <AccordionSummary expandIcon={<ExpandMoreIcon />} >
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: "row",
                    width: '100%'
                }}>
                    <Typography variant="h5" noWrap>
                        {sg.name}
                    </Typography>

                    <div
                        className={'sourceGroupControls'}
                        style={{
                            marginLeft: 'auto'
                        }}
                    >
                        <Tooltip title="Configure Source Group">
                            <IconButton color="primary" aria-label="source group settings" component="span" onClick={(e: any)=>{
                                e.stopPropagation();
                                setEdit(true);
                            }}>
                                <SettingsIcon
                                    fontSize={'large'}
                                />
                            </IconButton>
                        </Tooltip>
                    </div>
                </div>
            </AccordionSummary>

            <AccordionDetails>
                <Droppable key={sg.id} droppableId={`${sg.id}`}>
                    {(provided, snapshot) => (
                        <div
                            ref={provided.innerRef}
                            style={{...getListStyle(snapshot.isDraggingOver), width: '100%' }}
                            {...provided.droppableProps}
                        >
                            {sources}
                            {provided.placeholder}
                            <Button
                                variant="outlined"
                                style={{marginTop: '10px', marginBottom: '4px'}}
                                onClick={addNewSource}
                            >
                                Add Source
                            </Button>
                        </div>
                    )}
                </Droppable>
            </AccordionDetails>
        </Accordion>
        {edit && <SourceGroupConfigModal open={edit} onClose={()=>setEdit(false)} sourceGroup={sg} />}
    </>
})


const SourceDraggableEle = observer((props: {source: SourceInterface, idx: number, sourceGroupID: number}) => {
    return <Draggable
        key={props.source.id}
        draggableId={`${props.source.id}`}
        index={props.idx}
    >
        {(provided, snapshot) => (
            <SourceEle source={props.source} provided={provided} snapshot={snapshot} sourceGroupID={props.sourceGroupID} />
        )}
    </Draggable>
})

const SourceEle = observer((props: {source: SourceInterface, provided: DraggableProvided, snapshot: DraggableStateSnapshot, sourceGroupID: number}) => {
    const {provided, snapshot, source} = props;
    const [hovered, setHovered] = useState(false);

    const getItemStyle = (isDragging: boolean, draggableStyle: any) => ({
        // some basic styles to make the items look a bit nicer
        userSelect: "none",

        // change background colour if dragging
        background: isDragging ? "rgba(255,255,255,.5)" : "",

        // styles we need to apply on draggables
        ...draggableStyle
    });

    return <div
        ref={provided.innerRef}
        {...provided.draggableProps}
        {...provided.dragHandleProps}
        style={{
            ...getItemStyle(
                snapshot.isDragging,
                provided.draggableProps.style
            ),
            border: '1px solid black',
            borderRadius: '3px',
            paddingLeft: '3px',
            marginBottom: '3px',
            display: "flex",
            flexDirection: "row",
            maxWidth: '100%',
            overflow: 'hidden',
        }}
        onMouseOver={()=>setHovered(true)}
        onMouseLeave={()=>setHovered(false)}
    >
        <div style={{maxWidth: '100%', overflow: 'hidden'}}>
            <Typography noWrap>
                {source.name}
            </Typography>
            <Typography style={{marginLeft: '10px', fontStyle: 'italic'}} noWrap>
                Type: {source.type}
            </Typography>
        </div>
        <SourceControlButtons source={source} visible={hovered} sourceGroupID={props.sourceGroupID}/>
    </div>
})

export const SourceControlButtons = observer((props: {source: SourceInterface, visible: boolean, sourceGroupID: number}) => {
    const [edit, setEdit] = useState(false);

    return <>
        <div
            className={'SourceControlWrapper'}
            style={{
                marginLeft: 'auto',
                display: props.visible ? 'flex' : 'none',
                alignItems: 'center',
                justifyContent: 'center'
            }}
        >
            <Tooltip title="Configure Source" TransitionComponent={Fade} TransitionProps={{ timeout: 0 }}>
                <IconButton color="primary" aria-label="source settings" component="span" onClick={()=>setEdit(true)}>
                    <SettingsIcon
                        fontSize={'small'}
                    />
                </IconButton>
            </Tooltip>
            <Tooltip title="Drag" TransitionComponent={Fade} TransitionProps={{ timeout: 0 }}>
                <DragIndicatorIcon
                    fontSize={'large'}
                />
            </Tooltip>
        </div>
        {edit && <SourceConfigModal open={edit} onClose={() => setEdit(false)} source={props.source} sourceGroupID={props.sourceGroupID}/>}
    </>
});

/**
 * Create a blank Source with a new unique ID, which should be configured by the user.
 */
function createNewSource(): SourceInterface {
    let max = 0;
    SOURCE_GROUPS.forEach(sg => sg.sources.forEach(s => max = Math.max(max, s.id + 1)));

    return {
        dataJSON: "{}",
        id: max,
        name: "",
        type: SourceTypes.SAVED_POSTS
    }
}
