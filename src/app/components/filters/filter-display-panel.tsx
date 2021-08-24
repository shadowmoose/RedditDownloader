import {observer} from "mobx-react-lite";
import {SourceGroupInterface} from "../../../shared/source-interfaces";
import React, {useState} from "react";
import {
    Button,
    Collapse,
    FormControlLabel,
    Grid,
    MenuItem,
    Paper,
    Select,
    Switch,
    TextField,
    Tooltip
} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import FilterInterface, {
    CommentFilters,
    ComparatorKeyTypes, FilterComparators,
    FilterPropTypes,
    SubmissionFilters
} from "../../../shared/filter-interface";
import {BoundNumberInput} from "../input-components/number-input";
import DeleteIcon from '@material-ui/icons/Delete';
import IconButton from "@material-ui/core/IconButton";


export const FilterDisplayPanel = (props: {sourceGroup: SourceGroupInterface}) => {
    return <div className={'FilterDisplayPanel'}>
        <Typography variant="h5" align={'center'}>
            Manage Filters
        </Typography>
        <AddFilterPane sourceGroup={props.sourceGroup} />
        <ActiveFilterListPane sg={props.sourceGroup} filters={props.sourceGroup.filters} />
    </div>
};

const AddFilterPane = observer((props: {sourceGroup: SourceGroupInterface}) => {
    const [visible, setVisible] = useState(false);
    const [type, setType] = useState('submission');
    const [negative, setNegative] = useState('false');
    const [comparator, setComparator] = useState<ComparatorKeyTypes>('=');
    const [property, setProperty] = useState({name: 'author', value: ''});

    const propOpts = type === 'submission' ? SubmissionFilters : CommentFilters;
    const propMenuOpts = Object.keys(propOpts).map( key => {
        const {displayName} = propOpts[key as keyof typeof propOpts];
        return <MenuItem value={key} key={key}>{displayName}</MenuItem>;
    });

    if (!propOpts[property.name as keyof typeof propOpts]) { // switched post type, and old property name is now invalid
        setNewDefaultProperty('author');
        return <div />
    }
    const propType = propOpts[property.name as keyof typeof propOpts].type;


    function setNewDefaultProperty(propName: string) {
        const propType = propOpts[propName as keyof typeof propOpts].type;
        switch (propType) {
            case "datetime":
                return updateProperty(propName, Math.floor(Date.now()/1000));
            case "string":
                return updateProperty(propName, '');
            case "number":
                return updateProperty(propName, 0);
            case "boolean":
                return updateProperty(propName, true);
        }
    }

    function updateProperty(name: string, value: any) {
        setProperty({
            name,
            value
        });
    }

    function createFilter() {
        const newFilter: Partial<FilterInterface> = {
            comparator,
            field: property.name,
            forSubmissions: type === 'submission',
            negativeMatch: negative === 'true',
            valueJSON: JSON.stringify(property.value)
        };

        props.sourceGroup.filters.push(newFilter as FilterInterface);

        setVisible(false);
    }

    return <div>
        <Button
            style={{display: visible ? 'none' : 'block'}}
            variant="contained"
            color="primary"
            onClick = {() => {setVisible(true)}}
        >
            Add New Filter
        </Button>
        <Collapse in={visible} timeout="auto" unmountOnExit>
            <Paper variant={'outlined'} style={{padding: '10px'}}>
                Accept
                <Select
                    value={type}
                    onChange={(e: any) => setType(e.target.value)}
                    style={{margin: '5px'}}
                >
                    <MenuItem value={'submission'}>Submissions</MenuItem>
                    <MenuItem value={'comment'}>Comments</MenuItem>
                </Select>
                <br />
                where
                <Select
                    value={property.name}
                    onChange={(e: any) => setNewDefaultProperty(e.target.value)}
                    style={{margin: '5px'}}
                >
                    {propMenuOpts}
                </Select>

                <Select
                    value={negative}
                    onChange={(e: any) => setNegative(e.target.value)}
                    style={{margin: '5px'}}
                >
                    <MenuItem value={'false'}>is</MenuItem>
                    <MenuItem value={'true'}>is not</MenuItem>
                </Select>


                <Select
                    value={comparator}
                    onChange={(e: any) => setComparator(e.target.value)}
                    style={{margin: '5px'}}
                >
                    {Object.keys(FilterComparators).map(key => {
                        return <MenuItem value={key} key={key}>{FilterComparators[key as ComparatorKeyTypes]}</MenuItem>
                    })}
                </Select>

                <TypedFilterValueInput type={propType} value={property.value} onChange={val => updateProperty(property.name, val)}/>

                <div style={{marginTop: '15px', display: 'flex', justifyContent: 'space-between'}}>
                    <Button
                        disabled={!type || !property.name || !comparator || `${property.value}`.trim() === ''}
                        variant="contained"
                        color="primary"
                        onClick = {createFilter}
                    >
                        Add
                    </Button>

                    <Button
                        variant="contained"
                        color="secondary"
                        onClick = {() => {setVisible(false)}}
                    >
                        Cancel
                    </Button>
                </div>
            </Paper>
        </Collapse>
    </div>
});


const TypedFilterValueInput = (props: {type: FilterPropTypes, value: any, onChange: (val: any) => any}) => {
    switch (props.type) {
        case "boolean":
            return <FormControlLabel
                control={<Switch onChange={() => props.onChange(!props.value)} checked={!!props.value} />}
                label={`${props.value}`}
            />
        case "number":
            return <BoundNumberInput label={""} value={props.value} onUpdate={v => props.onChange(v)} />;
        case "string":
            return <TextField style={{marginTop: '5px'}} onChange={e => props.onChange(e.target.value)} value={props.value} />
        case "datetime":
            return <TextField
                style={{marginTop: '5px'}}
                type="datetime-local"
                value={dateString(new Date(props.value*1000))}
                onChange={e => {
                    props.onChange(Math.floor((new Date(e.target.value).valueOf()||Date.now())/1000))
                }}
            />
        default:
            throw Error(`Unknown filter property type: ${props.type}`)
    }
};


function dateString(date: Date) {
    const padded = (val: any, len=2) => `${val}`.padStart(len, '0');
    return padded(date.getFullYear(), 4) + "-" + padded(date.getMonth()+1) + "-" + padded(date.getDate()) + "T" + padded(date.getHours()) + ":" + padded(date.getMinutes()) + ":" + padded(date.getSeconds())
}


const ActiveFilterListPane = observer((props: {sg: SourceGroupInterface, filters: FilterInterface[]}) => {
    const submissions = buildDisplayFilterList(props.sg, props.filters.filter(f => f.forSubmissions), SubmissionFilters);
    const comments = buildDisplayFilterList(props.sg, props.filters.filter(f => !f.forSubmissions), CommentFilters);

    return <div style={{maxHeight: '310px', overflowY: 'auto'}}>
        <Typography variant="h6">Submissions</Typography>
        {submissions.length ? submissions : 'No limits on Submissions.'}
        <Typography variant="h6">Comments</Typography>
        {comments.length ? comments : 'No limits on Comments.'}
    </div>;
});


function buildDisplayFilterList(sg: SourceGroupInterface, filters: FilterInterface[], fType: typeof SubmissionFilters| typeof CommentFilters) {
    return filters.map(f => {
        const dName = fType[f.field as keyof typeof fType].displayName;
        const comp = FilterComparators[f.comparator];

        return <Grid container direction="row" alignItems="center" key={f.id || Math.random()} >
            <Tooltip title="Delete">
                <IconButton color="secondary" aria-label='delete' onClick={() => {
                    sg.filters = sg.filters.filter(fi => JSON.stringify(fi) !== JSON.stringify(f));
                }}>
                    <DeleteIcon />
                </IconButton>
            </Tooltip>
            {`${dName} is ${f.negativeMatch ? 'NOT' : ''} ${comp} [${JSON.parse(f.valueJSON)}]`}
        </Grid>
    });
}
