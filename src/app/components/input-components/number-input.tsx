import {observer} from "mobx-react-lite";
import {TextField} from "@material-ui/core";
import React from "react";

/**
 * A numeric input, which cleanly allows the user to enter integer-only values,
 * while formatting a bit better than a standard number-only field.
 *
 * Any returned values will be between 0 and the given max, inclusive.
 */
export const BoundNumberInput = observer((props: {
    limit?: number,
    label: string,
    value: number,
    onUpdate: (val: number)=>void
}) => {
    function setLimit(lim: string) {
        let l = lim.replace(/^0+/, '').replace(/\D/, '');
        props.onUpdate(Math.min(props.limit || Infinity, parseInt(l) || 0));
    }

    return <TextField
        label={props.label}
        variant="outlined"
        style={{width: '100%', marginBottom: '20px'}}
        value={props.value || 0}
        onChange={(e) => setLimit(e.target.value)}
    />
})
