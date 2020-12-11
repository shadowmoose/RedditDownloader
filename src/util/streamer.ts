
const TIMEOUT = Symbol('timeout');
const metaMap = new WeakMap<object, Record<string, DecoratorMetadata>>();

export interface ProxyOpts {
    onChange: (path: (string|number)[], target: any, newValue: any, metadata: DecoratorMetadata)=>void;
    onDelete: (path: (string|number)[], metadata: DecoratorMetadata)=>void;
}
export interface UpdateInfo {
    path: (string|number)[];
    value: any;
    deleted: boolean;
    customMetadata?: any;
}
export type SendFunction = (upd: UpdateInfo) => void;
interface DecoratorMetadata {
    delay?: number;
    before?: boolean;
    after?: boolean;
    customData?: any;
}
interface TrackerData {
    timer: any;
    dirty: boolean;
}
interface PendingTrackerData {
    earlier: boolean;
    data: TrackerData;
}

/**
 * Wrap the given object in a recursive Proxy, which wraps all non-primitive values in another nested Proxy.
 *
 * Automatically keeps track of the current path to the property referenced,
 * and loads metadata stored from any decorators used on the properties.
 *
 * Supports callbacks for whenever any nested property is set or deleted.
 */
export function proxify<T>(target: T, opts: ProxyOpts, tracker: (string|number)[] = [], metadata?: any): T {
    const path = (sp: PropertyKey): (string|number)[] => {
        // @ts-ignore
        return [...tracker, Number.isInteger(sp) ? sp : sp.toString()];
    }
    const getMeta = (key: PropertyKey) => {
        // @ts-ignore
        const proto = target?.__proto__;
        const mDat = metaMap.get(proto.constructor) || null;
        return mDat ? mDat[key.toString()] : null;
    }
    // @ts-ignore
    return new Proxy(target, {
        get(target: any, property) {
            const item = target[property];
            if (item && typeof item === 'object') {
                return proxify(item, opts, path(property), getMeta(property));
            }
            return item;
        },
        set(target: any, property, newValue) {
            if (target[property] === newValue) return true;
            target[property] = newValue;
            if (!(Array.isArray(target) && property === 'length')) {
                const prop = Number(property) in target ? Number(property) : property;
                // Pass either the current metadata value, or attempt to look one up (if we're the root object)
                opts.onChange(path(prop), target, newValue, metadata || getMeta(property));
            }
            return true;
        },
        deleteProperty(target, property) {
            opts.onDelete(path(property), metadata || getMeta(property));
            return true;
        }
    })
}

/**
 * Wraps the given Object in a Proxy, and broadcasts any (recursive) changes.
 */
export class Streamer <T>{
    private pending: Record<any, any> = {};
    public state: T;
    private send: SendFunction;

    constructor(state: T, sendFunction = console.info) {
        this.state = proxify(state, {
            onChange: this.onChange.bind(this),
            onDelete: this.onDelete.bind(this)
        });
        this.send = sendFunction;
    }

    public setSender(sender: SendFunction) {
        this.send = sender;
    }

    /**
     * Get all scheduled timers along the given path, and then all branching above the path's end.
     * @private
     */
    private getPending(path: any[], base: any = this.pending, ret: PendingTrackerData[] = [], idx = 0): PendingTrackerData[] {
        if (base[TIMEOUT]) {
            ret.push({
                data: base[TIMEOUT],
                earlier: idx <= path.length,
            });
        }

        if (idx < path.length) {
            const key = path[idx];
            const val = base[key];
            if (!val) return ret;
            this.getPending(path, val, ret, idx+1);
        } else {
            for (const k of Object.getOwnPropertyNames(base)) {
                this.getPending(path, base[k], ret, idx+1);
            }
        }
        return ret;
    }

    /**
     * Removes the Timer ID from the pending tree. Does not clear the actual timer.
     * Does not clear recursively to the root, but instead deletes the timer ID and wrapper object.
     * This is used for self-cleanup once a timer has finished.
     *
     * eg: `remove(['obj','a']) -> ['obj']`
     * @param path
     */
    removePending(path: any[]) {
        let curr: any = this.pending;
        let i;
        for (i = 0; i < path.length - 1; i++) {
            curr = curr[path[i]];
            if (!curr) return;
        }
        delete curr[path[i]];
    }

    getValue(path: any[]) {
        let curr: any = this.state;
        for (const p of path) {
            curr = curr[p];
        }
        return curr;
    }

    /**
     * Set a pending outgoing notification that will broadcast the value at the given path.
     * Unless specified otherwise, skips scheduling an alert if there is a lower-level alert already pending.
     * Automatically cancels any pending higher-level alerts.
     * @private
     */
    private setPending(path: any[], isDeleted: boolean, metadata: DecoratorMetadata) {
        const scheduled = this.getPending(path);

        for (const s of scheduled) {
            if (s.earlier) {
                s.data.dirty = true;
                return;
            }
            clearTimeout(s.data.timer)
        }

        let curr: any = this.pending;
        for (const p of path) {
            curr = curr[p] = curr[p] || {}
        }

        for (const k of Object.getOwnPropertyNames(curr)) {
            delete curr[k]; // Cull tree above this new, most recent update.
        }

        let dirty = true;

        if (metadata.before) {
            this.sendChange(path, isDeleted, metadata);
            dirty = false;
        }

        const data: TrackerData = {
            timer: 0,
            dirty
        };

        data.timer = setTimeout(() => {
            const after = metadata.after || (!metadata.after && !metadata.before);

            if (after && data.dirty) {
                this.sendChange(path, isDeleted, metadata);
            }
            this.removePending(path);
        }, metadata.delay || 0);

        curr[TIMEOUT] = data;
    }

    private onChange(path: (string | number)[], _target: any, _newValue: any, metadata: DecoratorMetadata) {
        this.setPending(path, false, metadata || {});
    }

    private onDelete(path: (string | number)[], metadata: DecoratorMetadata) {
        this.setPending(path, true, metadata || {});
    }

    sendChange(path: (string | number)[], deleted: boolean, metadata: DecoratorMetadata) {
        const data: UpdateInfo = {
            deleted,
            path: path,
            value: deleted ? undefined : this.getValue(path),
        };
        if (metadata.customData) data.customMetadata = metadata.customData;
        this.send(data);
    }

    /**
     * Attaches metadata to a weakly-linked metadata object, specific to this instance's class and property.
     * @param targetClass The Class that is being targeted.
     * @param propertyName The name of the property to build metadata for.
     * @param value The new Metadata to use.
     * @private
     */
    private static setMetadata(targetClass: any, propertyName: string, value: Partial<DecoratorMetadata>) {
        const con = targetClass.constructor;
        if (con) {
            const md = metaMap.get(con) || {};
            const existing: DecoratorMetadata = md[propertyName] || {};
            md[propertyName] = {...existing, ...value};
            metaMap.set(con, md);
        }
    }

    /**
     * A decorator, used to tag any properties in a Class that should be throttled.
     *
     * While awaiting this delay, subsequent updates to this property will not be scheduled.
     * At the end of the delay, the latest value will be send.
     */
    static delay(durationMS: number = 0) {
        return (targetClass: any, propertyKey: string) => {
            Streamer.setMetadata(targetClass, propertyKey, {
                delay: durationMS,
                after: true
            });
        }
    }

    /**
     * A decorator, used to tag any properties in a Class that should be throttled.
     *
     * Updates to the tagged property will be instantly sent.
     * Subsequent updates will not send during the timeout.
     * As the timeout finishes, another update will be sent if the value has changed since the initial send.
     *
     * NOTE: There is currently an issue with this decorator:
     * Sending a new value right after the previous send timer finishes will not properly respect the desired timer.
     */
    static throttle(durationMS: number = 0) {
        return (targetClass: any, propertyKey: string) => {
            Streamer.setMetadata(targetClass, propertyKey, {
                delay: durationMS,
                before: true,
                after: true
            });
        }
    }

    /**
     * A decorator, used to tag the given property with custom data.
     *
     * This data will be passed back out to the custom `send` method provided to each Streamer,
     * whenever this property changes.
     */
    static customMetadata(customData: any) {
        return (targetClass: any, propertyKey: string) => {
            Streamer.setMetadata(targetClass, propertyKey, {
                customData
            });
        }
    }
}
