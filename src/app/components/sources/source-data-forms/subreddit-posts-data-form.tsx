import {observer} from "mobx-react-lite";
import React from "react";
import {TextField} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import SubredditPostsSchema from "../../../../shared/source-schemas/subreddit-posts-schema";
import {BoundNumberInput} from "../../input-components/number-input";
import {SubmissionSortSelector} from "../../input-components/submission-sort-selector";


export const SubredditPostsDataForm = observer((props: {data: SubredditPostsSchema}) => {
    const data = props.data;

    function setSubreddits(input: string) {
        data.subreddit = input.replace('/r/', '');
    }

    return <div>
        <Divider style={{marginBottom: '10px', marginTop: '10px'}}/>

        <Typography style={{fontStyle: 'italic', fontSize: '14px', marginBottom: '20px'}} align={'center'}>
            Downloads Submissions from a list of Subreddits.
        </Typography>

        <TextField
            label="Enter a comma-separated list of subreddits to scrape"
            variant="outlined"
            onChange={(e)=> setSubreddits(e.target.value)}
            value={data.subreddit || ''}
            style={{width: '100%', marginBottom: '20px'}}
        />

        <SubmissionSortSelector onUpdate={(val, time) => {data.sort = val; data.time = time}} />

        <BoundNumberInput label="Limit number of submissions (0 for unlimited)" value={data.limit} onUpdate={val => data.limit = val} limit={1000} />
    </div>
})
