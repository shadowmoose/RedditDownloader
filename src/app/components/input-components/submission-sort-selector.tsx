import {observer} from "mobx-react-lite";
import React, {useState} from "react";
import {SubredditSorts, TimeRange} from "../../../shared/source-interfaces";
import {
    FormControl,
    FormControlLabel,
    FormLabel,
    InputLabel,
    MenuItem,
    Radio,
    RadioGroup,
    Select
} from "@material-ui/core";

/**
 * A selector input to allow the user to choose how they would like Submissions ordered, using Reddit terminology.
 */
export const SubmissionSortSelector = observer((props: {
    onUpdate: (val: SubredditSorts, time: TimeRange, isValidTimeSort: boolean)=>void
}) => {
    const [selected, setSelected] = useState('top');
    const [timeLimit, setTimeLimit] = useState(TimeRange[0]);
    const isValidRange = selected === 'top';

    function update(ev: any) {
        setSelected(ev.target.value);
        props.onUpdate(ev.target.value, timeLimit as TimeRange, isValidRange);
    }

    function updateTimeRange(val: string) {
        setTimeLimit(val);
        props.onUpdate(selected as SubredditSorts, val as TimeRange, isValidRange);
    }

    const options = SubredditSorts.map(s => {
        return <FormControlLabel value={s} control={
            <Radio
                checked={selected === s}
                onChange={()=>setSelected(s)}
                value={s}
                inputProps={{ 'aria-label': s }}
            />
        } key={s} label={s} />
    });

    const times = TimeRange.map(t => {
        return <MenuItem value={t} key={t}>Last {t.substr(0,1).toUpperCase()+t.substr(1)}</MenuItem>
    })

    return <div>
        <FormControl component="fieldset" style={{marginBottom: '20px'}}>
            <FormLabel component="legend">Sort Submissions By</FormLabel>
            <RadioGroup aria-label="sort posts" value={selected} onChange={update} row>
                {options}
            </RadioGroup>
        </FormControl>
        <FormControl component="fieldset" style={{marginBottom: '20px', width: '200px'}}>
            <InputLabel id="select-submission-time-range">Time range</InputLabel>
            <Select
                value={timeLimit}
                labelId="select-submission-time-range"
                onChange={e => updateTimeRange(e.target.value as string)}
                disabled={selected !== 'top'}
                style={{display: 'inline'}}
            >
                {times}
            </Select>
        </FormControl>
    </div>
});
