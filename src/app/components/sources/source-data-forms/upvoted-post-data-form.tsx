import {observer} from "mobx-react-lite";
import React from "react";
import UpvotedPostsSchema from "../../../../shared/source-schemas/upvoted-posts-schema";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import {BoundNumberInput} from "../../input-components/number-input";


export const UpvotedPostDataForm = observer((props: {data: UpvotedPostsSchema}) => {
    const data = props.data;

    return <div>
        <Divider style={{marginBottom: '10px', marginTop: '10px'}}/>

        <Typography style={{fontStyle: 'italic', fontSize: '14px', marginBottom: '20px'}} align={'center'}>
            Downloads any Submissions you have personally upvoted.
        </Typography>

        <BoundNumberInput label="Limit number of submissions (0 for unlimited)" value={data.limit} onUpdate={val => data.limit = val} limit={1000} />
    </div>
})
