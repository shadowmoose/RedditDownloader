import React from 'react';
import {observer} from "mobx-react-lite";
import {sendCommand, SOURCE_GROUPS} from "../../app-util/app-socket";
import Typography from "@material-ui/core/Typography";
import {DragDropContext, Draggable, Droppable, DropResult} from "react-beautiful-dnd";
import {ClientCommandTypes} from "../../../shared/socket-packets";
import {Button} from "@material-ui/core";


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


export const SourceGroupEle = observer((props: {sourceGroup: any}) => {
    const sg = props.sourceGroup;

    const sources = sg.sources.map((s: any, idx: number) => {
        return <SourceEle source={s} key={s.id} idx={idx} />
    });

    const getListStyle = (isDraggingOver: boolean) => ({
        background: isDraggingOver ? "rgba(0,0,0,.2)" : ''
    });

    return <div style={{paddingLeft: '10px', paddingRight: '10px',  background: sg.color}} className={'SourceGroupEle'}>
        <Typography variant="h4" noWrap>
            {sg.name}
        </Typography>

        <Droppable key={sg.id} droppableId={`${sg.id}`}>
            {(provided, snapshot) => (
                <div
                    ref={provided.innerRef}
                    style={getListStyle(snapshot.isDraggingOver)}
                    {...provided.droppableProps}
                >
                    {sources}
                    {provided.placeholder}
                    <Button variant="outlined" style={{marginTop: '10px', marginBottom: '4px'}}>Add Source</Button>
                </div>
            )}
        </Droppable>
    </div>
})


export const SourceEle = observer((props: {source: any, idx: number}) => {
    const src: any = props.source;

    const getItemStyle = (isDragging: boolean, draggableStyle: any) => ({
        // some basic styles to make the items look a bit nicer
        userSelect: "none",

        // change background colour if dragging
        background: isDragging ? "rgba(255,255,255,.5)" : "",

        // styles we need to apply on draggables
        ...draggableStyle
    });

    return <Draggable
        key={src.id}
        draggableId={`${src.id}`}
        index={props.idx}
    >
        {(provided, snapshot) => (
            <div
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
                style={getItemStyle(
                    snapshot.isDragging,
                    provided.draggableProps.style
                )}
            >
                <Typography variant="h6" noWrap>
                    {src.name}
                </Typography>
                <Typography style={{marginLeft: '10px'}} noWrap>
                    Type: {src.type}
                </Typography>
            </div>
        )}
    </Draggable>
})
