import React, {useEffect, useState} from "react";
import {sendCommand, useRmdState} from "../../../app-util/app-socket";
import {ClientCommandTypes} from "../../../../shared/socket-packets";
import {createStyles, makeStyles} from "@material-ui/core/styles";
import FindReplaceIcon from '@material-ui/icons/FindReplace';
import SortIcon from '@material-ui/icons/Sort';
import {
    DownloadSearchResponse,
    DownloadSearchResult,
    SearchableField,
    searchableFieldsList,
    SearchCommand
} from "../../../../shared/search-interfaces";
import {ArrowDownward, ArrowUpward} from "@material-ui/icons";
import AudiotrackIcon from '@material-ui/icons/Audiotrack';
import Typography from "@material-ui/core/Typography";
import Pagination from '@material-ui/lab/Pagination';
import {RMDStatus} from "../../../../shared/state-interfaces";
import RefreshIcon from '@material-ui/icons/Refresh';
import {Box, Fab, FormControl, Grid, InputLabel, MenuItem, Select, TextField, Tooltip} from "@material-ui/core";
import {observer} from "mobx-react-lite";
import BrowserSettings from "../../../app-util/local-config";


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

const MAX_MEDIA_SIZE = 200;


const BasicGalleryBody = observer(() => {
    const classes = useStyles();
    const [paging, setPaging] = useState<PagingType>({limit: BrowserSettings.resultsPerPage, offset: 0});
    const [searchCommand, setSearchCommand] = useState<SearchCommand>({
        offset: 0,
        limit: 10,
        where: [],
        ascending: true,
        matchAll: false,
        order: 'title'
    });
    const [searchResult, setSearchResult] = useState<DownloadSearchResponse>({
        count: 0,
        downloads: []
    });
    const [useSimpleSearch, setUseSimpleSearch] = useState(true);
    const fullCommand: SearchCommand = {
        ...searchCommand,
        ...paging
    };

    useEffect(() => {
        sendCommand(ClientCommandTypes.LIST_DOWNLOADS, fullCommand).then(res => {
            setSearchResult(res);
        });
        BrowserSettings.resultsPerPage = paging.limit;
    }, [JSON.stringify(fullCommand), JSON.stringify(paging)]);


    function toggleSearch() {
        setUseSimpleSearch(!useSimpleSearch);
    }

    function onSearch(search: SearchCommand) {
        setPaging({
            ...paging,
            offset: 0
        });
        setSearchCommand(search);
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
                    <BasicGallerySearchAll value={searchCommand} onChange={onSearch} /> :
                    <BasicGallerySearchCustom value={searchCommand} onChange={onSearch} />
                }
                <BasicGalleryPagingSelector totalResults={searchResult.count} paging={paging} onUpdate={setPaging} />
            </Grid>
        </div>

        <Box className={classes.root}>
            {searchResult.downloads.map((item) => (
                <div className={classes.mediaWrapper} key={item.dlUID}>
                    <GenericMediaDisplay dl={item} maxSize={MAX_MEDIA_SIZE} thumbnail={true}/>
                </div>
            ))}
        </Box>
    </Box>
});

export default BasicGalleryBody;


type PagingType = {limit: number, offset: number};

function BasicGalleryPagingSelector (props: {totalResults: number, paging: {limit: number, offset: number}, onUpdate: (paging: PagingType)=>void}) {
    const {limit, offset} = props.paging;
    const {rmdState} = useRmdState();
    const currentPage = Math.floor(offset/limit);
    const totalPages = Math.ceil(props.totalResults/limit);

    function updateLimit(event: any) {
        const newLimit = parseInt(event.target.value);
        props.onUpdate({
            offset: Math.floor(offset/newLimit)*newLimit,
            limit: newLimit
        })
    }

    function updatePage(_event: any, page: number) {
        props.onUpdate({
            ...props.paging,
            offset: (page-1)*limit
        })
    }

    function sendRefresh() {
        const old = props.paging;

        props.onUpdate({
            ...old,
            offset: old.offset+1
        });

        setTimeout(() => props.onUpdate(old), 1);
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
                style={{marginLeft: 10}}
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
}


/**
 * Search all fields, accepting any matches.
 * @param props
 * @constructor
 */
function BasicGallerySearchAll(props: {value: SearchCommand, onChange: (data: SearchCommand) => void}) {
    const [term, setTerm] = useState<string>('');

    useEffect(() => {
        const to = setTimeout(() => {
            props.onChange({
                ...props.value,
                where: term ? searchableFieldsList.map(f => ({column: f, value: `%${term}%`})) : [],
                matchAll: false,
                order: 'title',
                ascending: true
            });
        }, 500);

        return ()=>clearTimeout(to);
    }, [term])

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
function BasicGallerySearchCustom(props: {value: SearchCommand, onChange: (data: SearchCommand) => void}) {
    const [searchData, setSearchData] = useState<Record<SearchableField, string>>({} as any);
    const [orderBy, setOrderBy] = useState<SearchableField|null>(null);
    const [sortAsc, setSortAsc] = useState(true);

    useEffect(() => {
        const to = setTimeout(() => {
            const data: SearchCommand = {
                offset: 0,
                limit: 10,
                where: searchableFieldsList.filter(k=>searchData[k]).map(k => {
                    return {
                        column: k,
                        value: `%${searchData[k]}%`
                    }
                }),
                order: orderBy || 'title',
                ascending: sortAsc,
                matchAll: true
            };

            props.onChange(data);
        }, 500);

        return ()=>clearTimeout(to);
    }, [JSON.stringify(searchData), orderBy, sortAsc]);

    function searchSetter(key: SearchableField) {
        return (val: any) => {
            setSearchData({
                ...searchData,
                [key]: val
            });
        }
    }

    function sortSetter(key: SearchableField) {
        return (val: boolean) => {
            setOrderBy(key);
            setSortAsc(val);
        }
    }

    const sorters = searchableFieldsList.map(f => {
        return <td key={f}>
            <SortSearchInput
                field={f}
                value={searchData[f] || ''}
                onChange={searchSetter(f)}
                sorted={orderBy === f}
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
}


function GenericMediaDisplay (props: {dl: DownloadSearchResult, maxSize: number|string, thumbnail?: boolean}) {
    const dl = props.dl;
    const type = dl.albumFiles?.firstFile.type || dl.type;
    const fileId = dl.albumFiles?.firstFile.id || dl.id;
    const thumnail = !!props.thumbnail;

    // TODO: Split into new file, and use multiple components to make this less wonky.
    // TODO: Add "Open Modal" logic for everything, including galleries.
    // TODO: Add icons to denote galleries/videos.

    function openFullscreen() {
        window.open(`/file/${fileId}`);
    }

    switch ((type || '').split('/')[0]) {
        case 'image':
            return <img
                src={`/file/${fileId}`}
                alt={`[${dl.author}] ${dl.title}`}
                key={fileId}
                style={{
                    maxWidth: props.maxSize,
                    maxHeight: props.maxSize,
                    height: 'auto',
                    border: '3px solid blue',
                    cursor: 'pointer'
                }}
                title={`[${dl.author}] ${dl.title}`}
                onClick={openFullscreen}
            />
        case 'video':
            // TODO: Look into custom player, maybe, for things like playback speed or sound editing.
            // TODO: Pause when off screen.
            return <video
                key={fileId}
                style={{
                    maxWidth: props.maxSize,
                    maxHeight: props.maxSize,
                    height: 'auto',
                    border: '3px solid green',
                    cursor: 'pointer'
                }}
                controls={!props.thumbnail}
                loop={true}
                title={`[${dl.author}] ${dl.title}`}
                autoPlay
                muted={thumnail}
                onClick={openFullscreen}
                playsInline={thumnail}
            >
                <source src={`/file/${fileId}`} type={type} />
            </video>
        case 'audio':
            return <div
                title={`[${dl.author}] ${dl.title}`}
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    maxWidth: props.maxSize,
                    maxHeight: props.maxSize,
                    justifyContent: 'center',
                    alignItems: 'center',
                    border: '3px solid orange',
                    cursor: 'pointer'
                }}
                onClick={openFullscreen}
            >
                <div>
                    <AudiotrackIcon style={{ fontSize: 40 }} />
                </div>
                <div style={{maxWidth: props.maxSize, wordWrap: "break-word"}}>
                    <Typography variant={'subtitle2'} noWrap>{dl.title}</Typography>
                </div>
            </div>
        default:
            return <div title={`[${dl.author}] ${dl.title}`} onClick={openFullscreen}>Cannot Display Media Type "{type}"</div>;
    }
}


export function SortSearchInput (props: {
    field: SearchableField,
    value: any,
    onChange: (val: any)=>void,
    sorted: boolean,
    onSort: (ascending: boolean)=>void
}) {
    const classes = useStyles();
    const [sortAsc, setSortAsc] = useState(false);

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
        <Tooltip title={`Sort results by ${props.field}`}>
            {props.sorted ? sortArrow : <SortIcon
                onClick={()=>props.onSort(sortAsc)}
                className={classes.sortIcon}
            />}
        </Tooltip>
    </div>
}
