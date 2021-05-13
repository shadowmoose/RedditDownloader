import Source from "./source";
import * as reddit from '../reddit/snoo';
import {SourceTypes} from "../../shared/source-interfaces";
import UpvotedPostsSchema from "../../shared/source-schemas/upvoted-posts-schema";

export default class UpvotedPostSource extends Source {
    protected data!: UpvotedPostsSchema;
    readonly type = SourceTypes.UPVOTED_POSTS;

    async *find() {
        const gen = reddit.getUpvoted(this.data.limit);

        return yield* gen;
    }
}
