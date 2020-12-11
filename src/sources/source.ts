import Ajv from "ajv"
import DBSource from "../database/entities/db-source";
import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";
import {SourceSchema} from "../shared/source-interfaces";

export default abstract class Source {
    protected abstract data: any;
    readonly abstract schema: SourceSchema;
    public readonly abstract type: string;
    public readonly abstract description: string;

    /**
     * Find the next post that this Source has available.
     */
    public abstract find(): AsyncGenerator<DBSubmission | DBComment>;

    /**
     * Builds a new instance of this class, using the given DB data.
     * Validates/coerces the given DB data against this source's schema.
     */
    public createFromDB(src: DBSource): this {
        const rt = Object.create(Object.getPrototypeOf(this));
        const ajv = new Ajv({ useDefaults: true, coerceTypes: true });
        const schema = { type: 'object', properties: this.schema };
        if (ajv.validate(schema, src.data)) {
            rt.data = src.data;
        } else {
            throw Error(ajv.errorsText(ajv.errors));
        }
        return rt;
    }
}

