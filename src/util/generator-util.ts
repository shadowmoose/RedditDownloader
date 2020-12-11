/**
 * Reads through a Generator, awaiting `cb` on each element.
 * If the returned result is truthy, that result is emitted. Otherwise, nothing is emitted.
 */
export async function* filterMap<T, TR, R>(gen: AsyncGenerator<T, TR>, cb: (ele: T) => R) {
    let count = 0;
    while (true) {
        const nxt = await gen.next();
        if (nxt.done) return count;

        const res = await cb(nxt.value);
        if (res) {
            count++;
            yield res as NonNullable<R>;
        }
    }
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
