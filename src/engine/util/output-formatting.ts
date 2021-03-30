/**
 * Prints out a display for the given array of objects, using their keys (in order of creation) as the header values.
 * The table is dynamically truncated to fit the current terminal width.
 * @param objs
 * @param hideHead
 * @param maxValLen The maximum width a single value may use, before being truncated.
 * @param spacing
 */
export function printTable(objs: Record<string, any>[], hideHead = false, maxValLen = 50, spacing = '  ') {
    const maxWidth = process.stdout.columns || 150;
    const toStr = (val: any) => {
        let r = (val === undefined || val === null) ? '' : `${val}`.trim();
        if (r.length > maxValLen) r = r.substring(0, maxValLen - 3) + '...';
        return r;
    }
    const upper = (val: string) => val.charAt(0).toUpperCase() + val.slice(1);
    const fit = (val: string) => val.length < maxWidth ? val : val.substring(0, maxWidth - 3) + '...';
    const keys: Record<string, number> = {};

    objs.forEach(o => {
        // Build table of column widths.
        Object.keys(o).forEach(k => {
            keys[k] = Math.max(keys[k] || (hideHead ? 0 : k.length), toStr(o[k]).length);
        });
    });

    console.log(process.stdout.columns, process.stdout.rows);

    const header = fit(spacing + Object.keys(keys).map(k => upper(k).replace('_', ' ').padEnd(keys[k])).join(spacing) + spacing);
    if (!hideHead) {
        console.log(''.padEnd(header.length, '-'))
        console.log(header);
        console.log(''.padEnd(header.length, '-'))
    }

    objs.forEach(o => {
        console.log(
            fit(spacing + Object.keys(keys).map(k => toStr(o[k]).padEnd(keys[k])).join(spacing).trimEnd())
        )
    })
    if (!hideHead) console.log(''.padEnd(header.length, '-'))
}
