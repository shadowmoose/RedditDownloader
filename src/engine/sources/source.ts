import DBSource from "../database/entities/db-source";
import DBSubmission from "../database/entities/db-submission";
import DBComment from "../database/entities/db-comment";
import {SourceTypes} from "../../shared/source-interfaces";

export default abstract class Source {
    protected abstract data: any;
    public readonly abstract type: SourceTypes;
    public alias: string = '';

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
        rt.data = src.data;
        rt.alias = src.name;
        return rt;
    }
}

