import Source from "./source";
import * as reddit from '../reddit/snoo';
import {SourceTypes} from "../../shared/source-interfaces";
import DBComment from "../database/entities/db-comment";
import {filterMap} from "../util/generator-util";
import SavedPostSourceSchema from "../../shared/source-schemas/saved-posts-schema";

export default class SavedPostSource extends Source {
    protected data!: SavedPostSourceSchema;
    readonly type: SourceTypes = SourceTypes.SAVED_POSTS;

    async *find() {
        const gen = reddit.getSavedPosts(this.data.limit);

        return yield* filterMap(gen, ele => {
            if (this.data.getComments || !(ele instanceof DBComment)) {
                return ele
            }
        })
    }
}
