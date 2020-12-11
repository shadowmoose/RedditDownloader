const logErr = (err: Error) => console.error(err);

/**
 * Repeatedly calls the given callback for a new Promise, until the provided `stop()` callback is called.
 * Waits to generate each Promise so that only a specified amount run concurrently.
 *
 * The entire Pool can be awaited, and will resolve once the feeder function calls `stop()`, and all pending promises finish.
 *
 * Note that if the feeder function is itself async, it may be called more than once after `stop` is triggered.
 *
 * @param feeder The function that should create and return new Promises. Call the provided `stop()` function to stop the pool.
 * @param concurrent Amount of Promises to run concurrently.
 * @param errHandler A callback to receive any otherwise uncaught errors. Defaults to logging.
 */
export default function promisePool(feeder: (stop: ()=>void, threadNumber: number)=>Promise<any>|null, concurrent: number, errHandler: (err: any)=>void = logErr) {
    const pool: Record<number, Promise<any>|null> = {};
    let count: number = 0;
    let stop = false;

    return new Promise<number>( resolve => {
        const popNext = async (idx: number) => {
            if (stop) {
                await Promise.all(Object.values(pool));
                return resolve(count);
            }

            const nxt = feeder(()=>{stop=true; count--;}, idx);
            count++;

            pool[idx] = Promise.resolve().then(()=>nxt).catch(errHandler).finally(() => {
                popNext(idx);
            })
        }

        for (let i = 0; i < concurrent; i++) {
            popNext(i).catch(errHandler);
        }
    });
}


/**
 * Returns the given function, but wrapped so that only one call may run concurrently.
 */
export function mutex<T,A extends any[]>(fn: (...args: A)=>T): (...args: A)=>Promise<T> {
    let p: Promise<any> = Promise.resolve();

    return (...args: A) => {
        p = p.then(() => fn(...args) );
        return p
    }
}


/**
 * Simple sleep function, just to save the trouble of retyping it.
 */
export async function sleep(ms: number) {
    return await new Promise(res => setTimeout(res, ms));
}
