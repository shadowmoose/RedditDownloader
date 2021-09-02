import {observer} from "mobx-react-lite";
import React, {useEffect} from "react";
import SavedPostSourceSchema from "../../../../shared/source-schemas/saved-posts-schema";
import {FormControlLabel, Switch} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";


export const SavedPostDataForm = observer((props: {data: SavedPostSourceSchema}) => {
    const data = props.data;

    useEffect(() => {
        if (!Object.keys(data).length) {
            const blank: SavedPostSourceSchema = {
                getComments: false,
                limit: 0
            };
            Object.assign(data, blank);
        }
    }, [props.data]);

    return <div>
        <Divider style={{marginBottom: '10px', marginTop: '10px'}}/>

        <Typography style={{fontStyle: 'italic', fontSize: '14px', marginBottom: '20px'}} align={'center'}>
            Downloads any Submissions and/or Comments you have personally saved.
        </Typography>

        <FormControlLabel
            control={
                <Switch
                    checked={Boolean(data.getComments)}
                    onChange={(e) => {data.getComments = e.target.checked}}
                    name="Get Comments"
                    inputProps={{ 'aria-label': 'Get comments' }}
                />
            }
            label="Also Load Saved Comments"
        />
    </div>
})
