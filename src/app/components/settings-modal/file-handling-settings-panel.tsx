import {observer} from "mobx-react-lite";
import React from "react";
import {
    FormControl,
    FormControlLabel,
    FormLabel,
    makeStyles,
    Radio,
    RadioGroup,
    Switch, TextField,
    Tooltip, Typography
} from "@material-ui/core";
import {SETTINGS} from "../../app-util/app-socket";
import {createStyles, Theme} from "@material-ui/core/styles";
import {AvailableTemplateTags, ExampleTagObject} from "../../../shared/name-template";


const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        switchOverlay: {
            marginLeft: '5px',
            paddingRight: '5px',
            backgroundColor: theme.palette.background.paper,
            transform: `translate(10px, 20px)`,
        },
        overlayedGroup: {
            padding: '5px',
            paddingTop: 25,
            paddingBottom: 15,
            border: '1px solid',
            borderRadius: '10px'
        }
    }),
);


export const FileHandlingSettingsPanel = observer(() => {
    return <div>
        <OutputTemplateSetting />
        <DedupeSettingsPanel />
    </div>
});


export const OutputTemplateSetting = observer(() => {
    let sample = `${SETTINGS.outputTemplate.trim()}.mp4`;
    AvailableTemplateTags.forEach(t => {
        sample = sample.replaceAll(`[${t}]`, `${ExampleTagObject[t as keyof typeof ExampleTagObject]}`)
    });

    return <div>
        <Tooltip title={`The relative output file path for everything RMD downloads. Supported tags are: ${AvailableTemplateTags.map(t=>`[${t}]`).join(', ')}`}>
            <TextField
                id="outlined-basic"
                label="Output Template"
                variant="outlined"
                style={{width: '100%'}}
                value={SETTINGS.outputTemplate}
                onChange={e=>SETTINGS.outputTemplate = e.target.value}
            />
        </Tooltip>
        <Typography variant="caption">
            <b>Sample: </b>{sample}
        </Typography>
    </div>
});


/**
 * Adjust the Minimum Similarity Deduplication setting.
 */
export const DedupeSettingsPanel = observer(() => {
    const dedupe = SETTINGS.dedupeFiles;
    const styles = useStyles();

    return <>
        <Tooltip title={'RMD can scan files after they are downloaded, and remove any duplicates. Additionally, it can optionally compare image visual similarity.'}>
            <FormControlLabel
                className={styles.switchOverlay}
                control={
                    <Switch
                        checked={SETTINGS.dedupeFiles}
                        onChange={ev => SETTINGS.dedupeFiles = ev.target.checked}
                        color={'primary'}
                        name="dedupeFilesSwitch"
                    />
                }
                label="Remove duplicate files"
            />
        </Tooltip>
        <div
            className={styles.overlayedGroup}
            style={{borderColor: dedupe ? 'black': 'gray'}}
        >
            <SymbolicLinkSetting dedupe={dedupe} />

            <SkipAlbumSetting dedupe={dedupe} />

            <SimiliaritySelector dedupe={dedupe} />
        </div>
    </>
});


/**
 * Adjust the Minimum Similarity Deduplication setting.
 */
export const SymbolicLinkSetting = observer((props: {dedupe: boolean}) => {
    return <Tooltip title={'If duplicate files should be replaced with symbolic links pointing to the original instead of only being deleted.'}>
        <FormControlLabel
            disabled={!props.dedupe}
            control={
                <Switch
                    color={'primary'}
                    checked={SETTINGS.createSymLinks}
                    onChange={ev => SETTINGS.createSymLinks = ev.target.checked}
                    name="createSimLinksSwitch"
                />
            }
            label="Create symbolic links for any duplicate files"
        />
    </Tooltip>
});


/**
 * Adjust the Minimum Similarity Deduplication setting.
 */
export const SkipAlbumSetting = observer((props: {dedupe: boolean}) => {
    return <Tooltip title={'If all files nested within albums should skip duplication checks.'}>
        <FormControlLabel
            disabled={!props.dedupe}
            control={
                <Switch
                    color={'primary'}
                    checked={SETTINGS.skipAlbumFiles}
                    onChange={ev => SETTINGS.skipAlbumFiles = ev.target.checked}
                    name="skipAlbumFilesSwitch"
                />
            }
            label="Don't check files inside albums"
        />
    </Tooltip>
});

/**
 * Adjust the Minimum Similarity Deduplication setting.
 */
export const SimiliaritySelector = observer((props: {dedupe: boolean}) => {
    return <FormControl
        component="fieldset"
        style={{
        marginTop: 10,
        alignItems: 'center',
        width: '100%'
    }}>
        <FormLabel >Image Visual Similarity Threshold</FormLabel>
        <Tooltip title={'Controls how similar two images must visually be before RMD assumes one is a duplicate. Be careful changing this: The less strict the filter, the more likely it is that images are falsely detected as duplicates.'}>
            <RadioGroup
                row
                aria-label="image threshold"
                value={''+SETTINGS.minimumSimiliarity}
                onChange={e => SETTINGS.minimumSimiliarity = parseInt(e.target.value)}
            >
                <FormControlLabel value="0" control={<Radio color="secondary" />} label="Disabled" disabled={!props.dedupe} />
                <FormControlLabel value="2" control={<Radio color="secondary" />} label="Very Strict" disabled={!props.dedupe} />
                <FormControlLabel value="3" control={<Radio color="secondary" />} label="Strict" disabled={!props.dedupe} />
                <FormControlLabel value="4" control={<Radio color="secondary" />} label="Very Lenient" disabled={!props.dedupe} />
            </RadioGroup>
        </Tooltip>
    </FormControl>
});
