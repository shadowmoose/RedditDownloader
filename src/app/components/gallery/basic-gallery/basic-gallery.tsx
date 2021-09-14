import React, {useEffect, useState} from "react";
import {sendCommand, useRmdState} from "../../../app-util/app-socket";
import {ClientCommandTypes} from "../../../../shared/socket-packets";
import {createStyles, makeStyles} from "@material-ui/core/styles";
import FindReplaceIcon from '@material-ui/icons/FindReplace';
import SortIcon from '@material-ui/icons/Sort';
import {
    DownloadSearchResponse,
    SearchableField,
    searchableFieldsList, SearchColumn,
    SearchCommand
} from "../../../../shared/search-interfaces";
import {ArrowDownward, ArrowUpward} from "@material-ui/icons";
import Pagination from '@material-ui/lab/Pagination';
import {RMDStatus} from "../../../../shared/state-interfaces";
import RefreshIcon from '@material-ui/icons/Refresh';
import {
    Box,
    Fab,
    FormControl,
    FormControlLabel,
    Grid,
    InputLabel,
    MenuItem,
    Select,
    Switch,
    TextField,
    Tooltip
} from "@material-ui/core";
import {observer} from "mobx-react-lite";
import BrowserSettings from "../../../app-util/local-config";
import {MediaWrapper} from "../media-wrapper";
import {observable} from "mobx";

const MAX_MEDIA_SIZE = 200;

export const SEARCH_OBJECT = observable<SearchCommand>({
    offset: 0,
    limit: BrowserSettings.resultsPerPage,
    where: [],
    order: 'id',
    ascending: true,
    matchAll: false
});

export function updateSearch(cmd: Partial<SearchCommand>) {
    Object.assign(SEARCH_OBJECT, cmd);
}


const useStyles = makeStyles(() =>
    createStyles({
        root: {
            display: 'flex',
            flexWrap: 'wrap',
            overflow: 'hidden',
        },
        mediaWrapper: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            width: MAX_MEDIA_SIZE,
            height: MAX_MEDIA_SIZE,
            marginRight: 10,
            marginBottom: 10,
            overflow: 'hidden'
        },
        sortIcon: {
            margin: 0,
            position: 'absolute',
            top: '50%',
            transform: 'translateY(-50%)',
            cursor: 'pointer',
        }
    })
);


const BasicGalleryBody = observer(() => {
    const classes = useStyles();
    const [searchResult, setSearchResult] = useState<DownloadSearchResponse>({
        count: 0,
        downloads: []
    });
    const [useSimpleSearch, setUseSimpleSearch] = useState(true);
    const [lastWhere, setLastWhere] = useState<SearchColumn[]>([]);

    useEffect(() => {
        const isNewWhere = JSON.stringify(lastWhere) !== JSON.stringify(SEARCH_OBJECT.where);

        const to = setTimeout(() => {
            sendCommand(ClientCommandTypes.LIST_DOWNLOADS, SEARCH_OBJECT).then(res => {
                setSearchResult(res);
            });
        }, isNewWhere ? 500 : 0);
        BrowserSettings.resultsPerPage = SEARCH_OBJECT.limit;

        setLastWhere(SEARCH_OBJECT.where);

        return ()=>clearTimeout(to);
    }, [JSON.stringify(SEARCH_OBJECT)]);

    useEffect(() => {
        SEARCH_OBJECT.where = [];
    }, [useSimpleSearch])


    function toggleSearch() {
        setUseSimpleSearch(!useSimpleSearch);
    }

    return <Box>
        <div id={"basic-search-toolbar"}>
            <Grid style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                marginBottom: 15
            }}>
                <Tooltip title={useSimpleSearch ? 'Switch to Advanced Search' : 'Switch to Simple Search'}>
                    <FindReplaceIcon
                        onClick={toggleSearch}
                        color={'primary'}
                        style={{cursor: 'pointer', marginRight: 10}}
                    />
                </Tooltip>

                {useSimpleSearch ?
                    <BasicGallerySearchAll /> :
                    <BasicGallerySearchCustom />
                }

                <AutoplayToggle />

                <BasicGalleryPagingSelector totalResults={searchResult.count} />
            </Grid>
        </div>

        <Box className={classes.root}>
            {searchResult.downloads.map((item) => (
                <div className={classes.mediaWrapper} key={item.dlUID}>
                    <MediaWrapper dl={item} maxSize={MAX_MEDIA_SIZE} />
                </div>
            ))}
        </Box>
    </Box>
});

export default BasicGalleryBody;


const BasicGalleryPagingSelector = observer((props: {totalResults: number}) => {
    const {limit, offset} = SEARCH_OBJECT;
    const {rmdState} = useRmdState();
    const currentPage = Math.floor(offset/limit);
    const totalPages = Math.ceil(props.totalResults/limit);

    function updateLimit(event: any) {
        const newLimit = parseInt(event.target.value);
        updateSearch({
            limit: newLimit
        })
    }

    function updatePage(_event: any, page: number) {
        updateSearch({
            offset: (page-1)*limit
        })
    }

    function sendRefresh() {
        const old = SEARCH_OBJECT.limit;

        updateSearch({
            limit: old+1
        });

        setTimeout(() => {
            updateSearch({
                limit: old
            })
        }, 1);
    }

    return <Grid
        style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            marginLeft: 15
        }}
    >
        <FormControl variant="outlined">
            <InputLabel id="select-page-result-count-label">Per Page</InputLabel>
            <Select
                label={"-Per Page:-"}
                labelId="select-page-result-count-label"
                id="select-page-result-count"
                value={limit}
                onChange={updateLimit}
                style={{marginLeft: 10, marginRight: 10}}
            >
                <MenuItem value={10}>10</MenuItem>
                <MenuItem value={25}>25</MenuItem>
                <MenuItem value={50}>50</MenuItem>
                <MenuItem value={100}>100</MenuItem>
                <MenuItem value={150}>150</MenuItem>
            </Select>
        </FormControl>

        {totalPages ? <Pagination count={totalPages} page={currentPage+1} onChange={updatePage} /> : null}
        {rmdState === RMDStatus.RUNNING && <Tooltip title={'RMD is actively adding new posts. Click to refresh search results.'}><Fab onClick={sendRefresh}><RefreshIcon /></Fab></Tooltip>}
    </Grid>
});


const AutoplayToggle = observer(() => {
    return <FormControlLabel
        style={{marginLeft: 10}}
        control={
            <Switch
                checked={BrowserSettings.autoPlayVideo}
                onChange={ev => BrowserSettings.autoPlayVideo = ev.target.checked}
                color={'primary'}
                name="autoplaySwitch"
            />
        }
        label="Autoplay"
    />
});


/**
 * Search all fields, accepting any matches.
 * @param props
 * @constructor
 */
function BasicGallerySearchAll(props: {}) {
    const [term, setTerm] = useState<string>('');

    useEffect(() => {
        updateSearch({
            where: term ? searchableFieldsList.map(f => ({column: f, value: `%${term}%`})) : [],
            matchAll: false,
            order: 'id',
            ascending: true
        });
    }, [term]);

    return <TextField
        onChange={e => setTerm(e.target.value)}
        value={term}
        label={"Search Downloaded Media"}
        variant={'outlined'}
    />
}

/**
 * Search specific fields, requiring every field to match.
 * @param props
 * @constructor
 */
const BasicGallerySearchCustom = observer(() => {
    const searchData: Record<string, string> = {};
    for (const w of SEARCH_OBJECT.where) {
        searchData[w.column as string] = w.value;
    }

    function searchSetter(key: SearchableField) {
        return (val: any) => {
            const ex = SEARCH_OBJECT.where.find(w => w.column === key);
            const value = `%${val}%`;

            if (ex) {
                ex.value = value;
            } else {
                SEARCH_OBJECT.where.push({
                    column: key,
                    value
                });
            }
        }
    }

    function sortSetter(key: SearchableField) {
        return (val: boolean) => {
            updateSearch({
                order: key,
                ascending: val
            })
        }
    }

    const sorters = searchableFieldsList.map(f => {
        return <td key={f}>
            <SortSearchInput
                field={f}
                value={(searchData[f] || '').replace(/^%|%$/gm, '')}
                onChange={searchSetter(f)}
                sorted={SEARCH_OBJECT.order === f}
                onSort={sortSetter(f)}
            />
        </td>
    });

    return <table style={{display: 'inline'}}>
        <tbody>
            <tr>
                {sorters}
            </tr>
        </tbody>
    </table>
});


export function SortSearchInput (props: {
    field: SearchableField,
    value: any,
    onChange: (val: any)=>void,
    sorted: boolean,
    onSort: (ascending: boolean)=>void
}) {
    const classes = useStyles();
    const [sortAsc, setSortAsc] = useState(true);

    function toggleSort() {
        props.onSort(!sortAsc);
        setSortAsc(!sortAsc);
    }

    const sortArrow = sortAsc ? <ArrowUpward className={classes.sortIcon} onClick={toggleSort}/> : <ArrowDownward className={classes.sortIcon} onClick={toggleSort}/>;

    return <div style={{position: 'relative', width: 120, marginRight: 10}}>
        <TextField
            onChange={e => props.onChange(e.target.value)}
            value={props.value}
            label={props.field}
            variant="outlined"
            size="small"
            style={{
                width: 100,
            }}
        />
        <Tooltip title={`Order results by ${props.field}`}>
            {props.sorted ? sortArrow : <SortIcon
                onClick={()=>props.onSort(sortAsc)}
                className={classes.sortIcon}
            />}
        </Tooltip>
    </div>
}
