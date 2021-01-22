import "reflect-metadata";
import {BaseEntity, getManager} from "typeorm";

// Hacky type templating to get a roughly-correct object, with all required properties inserted:
type Constructor<T> = { new (): T }
type ExcludeMethods<T extends {id?: any}> =
    Pick<T, {
        [K in keyof T]:
            T[K] extends (_: any) => any ? never // No functions.
            : undefined extends T[K] ? never     // No optionals.
            : Promise<any> extends T[K] ? never  // No Promises (references)
            : K extends 'id' ? never             // No ID field.
            : K
    }[keyof T]> & Partial<T>; // Include all other fields as optional.

export class DBEntity extends BaseEntity{
    /**
     * Build a new instance of this class, setting the required/optional values.
     */
    static build<T>(this: Constructor<T>, config: ExcludeMethods<T>): T {
        return Object.assign(new this(), config)
    }
}
