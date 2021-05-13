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
import {Accordion, AccordionDetails, AccordionSummary, Button, Fade, IconButton, Tooltip} from "@material-ui/core";
import SettingsIcon from '@material-ui/icons/Settings';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import DragIndicatorIcon from '@material-ui/icons/DragIndicator';
import {SourceGroupInterface, SourceInterface, SourceTypes} from "../../../shared/source-interfaces";
import {SourceEditorModal} from "./source-editor-modal";
import {observable} from "mobx";


export const SourceGroupDrawer = observer(() => {
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
    </DragDropContext>
});


export const SourceGroupEle = observer((props: {sourceGroup: SourceGroupInterface}) => {
    const sg = props.sourceGroup;
    const [newSource, setNewSource] = useState<SourceInterface|null>(null);

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
            console.log('Cancelled new source!')
            sg.sources.splice(sg.sources.findIndex(s=>s.id === newSource.id), 1);
        }
        setNewSource(null);
    }

    return <Accordion
        className={'SourceGroupEle'}
        TransitionProps={{ unmountOnExit: true }}
        defaultExpanded={true}
        style={{background: sg.color}}
    >
        {newSource && <SourceEditorModal open={!!newSource} onClose={onEditorClose} source={newSource} sourceGroupID={sg.id} />}
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
                        <SettingsIcon
                            fontSize={'large'}
                        />
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

export const SourceControlButtons = (props: {source: SourceInterface, visible: boolean, sourceGroupID: number}) => {
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
                <IconButton color="primary" aria-label="upload picture" component="span" onClick={()=>setEdit(true)}>
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
        {edit && <SourceEditorModal open={edit} onClose={() => setEdit(false)} source={props.source} sourceGroupID={props.sourceGroupID}/>}
    </>
}

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
