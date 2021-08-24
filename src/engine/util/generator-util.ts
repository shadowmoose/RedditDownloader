/**
 * Reads through a Generator, awaiting the given `cb` function on each element.
 * If the returned result is truthy, that result is emitted. Otherwise, nothing is emitted.
 */
export async function* filterMap<T, TR, R>(gen: AsyncGenerator<T, TR>, cb: (ele: T, stop: ()=>void) => R) {
    let count = 0;
    let stop = false;
    while (!stop) {
        const nxt = await gen.next();
        if (nxt.done) break;

        const res = await cb(nxt.value, ()=>stop = true);

        if (stop) break;

        if (res) {
            count++;
            yield res as NonNullable<R>;
        }
    }

    return count;
}

/**
 * Iterates a Generator, and runs the given callback for each element.
 * @returns The total count of elements iterated.
 */
export async function forGen<T>(gen: AsyncGenerator<T>, cb: (ele: T, idx: number, stop: Function)=> void) {
    let nxt = await gen.next();
    let found = 0;
    let stop = false;

    while (!nxt.done && !stop) {
        await cb(nxt.value, found, ()=>stop = true);
        found ++;
        nxt = await gen.next()
    }

    return found;
}
