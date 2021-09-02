import {observer} from "mobx-react-lite";
import {TextField, Tooltip} from "@material-ui/core";
import React, {useEffect, useState} from "react";

/**
 * A numeric input, which cleanly allows the user to enter integer-only values,
 * while formatting a bit better than a standard number-only field.
 *
 * Any returned values will be between 0 and the given max, inclusive.
 */
export const BoundNumberInput = observer((props: {
    maximum?: number,
    minimum?: number,
    variant?: string,
    label: string,
    value: number,
    onUpdate: (val: number)=>void,
    tooltip?: string,
    style?: React.CSSProperties
}) => {
    const [val, setVal] = useState(``);
    useEffect(() => setVal(`${props.value}`), [props.value]);

    function setLimit(lim: string) {
        lim = lim.replace(/\D/, '').trim();
        let l = `${lim ? parseInt(lim) : ''}`;

        setVal(l);
        if (lim !== '') {
            props.onUpdate(parseInt(l));
        }
    }

    return <Tooltip title={props.tooltip||''}>
        <TextField
            type={'number'}
            label={props.label}
            variant="outlined"
            style={{width: '100%', marginBottom: '20px', ...(props.style||{}) }}
            value={val}
            onChange={(e) => setLimit(e.target.value)}
            inputProps={{min: props.minimum, max: props.maximum}}
        />
    </Tooltip>
})
