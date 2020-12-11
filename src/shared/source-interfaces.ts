export enum TypeOpts {
    STRING = "string",
    NUMBER = "number",
    BOOLEAN = 'boolean',
}

/**
 * The schema used by each Source to control/coerce what types it accepts.
 */
export interface SourceSchema {
    [key: string]: {
        /** A user-friendly prompt for this input. */
        description: string;
        /** The data type that should be accepted. */
        type: TypeOpts;
        /** The default value this should return */
        default: any;
    }
}

/**
 * Some generally-applicable schema values for Sources.
 */
export const ListingOptionsSchema: SourceSchema = {
    limit: {
        description: 'Maximum amount of posts:',
        type: TypeOpts.NUMBER,
        default: 0
    }
};
