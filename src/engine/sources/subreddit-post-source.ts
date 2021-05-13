import Source from "./source";
import * as reddit from '../reddit/snoo';
import {SourceTypes} from "../../shared/source-interfaces";
import SubredditPostsSchema from "../../shared/source-schemas/subreddit-posts-schema";


export default class SubredditPostSource extends Source {
    protected data!: SubredditPostsSchema;
    readonly type = SourceTypes.SUBREDDIT_POSTS;

    async *find() {
        const gen = reddit.getSubreddit(this.data.subreddit, this.data.sort, this.data.time, this.data.limit);

        return yield* gen;
    }
}
