import Source from "./source";
import * as reddit from '../reddit/snoo';
import {ListingOptionsSchema, TypeOpts} from "../shared/source-interfaces";
import {SubredditSorts, TimeRange} from "../reddit/snoo";


export default class SubredditPostSource extends Source {
    protected data: any;
    readonly schema = {
        subreddit: {
            description: 'Subreddit to download:',
            type: TypeOpts.STRING,
            default: '',
            minLength: 1
        },
        type: {
            description: 'Sort submissions by:',
            type: TypeOpts.STRING,
            default: SubredditSorts[0],
            enum: SubredditSorts
        },
        time: {
            description: 'Time range:',
            type: TypeOpts.STRING,
            default: TimeRange[0],
            enum: TimeRange
        },
        ...ListingOptionsSchema
    };
    readonly description: string = `The submissions from a subreddit`;
    readonly type: string = 'subreddit-posts';

    async *find() {
        const gen = reddit.getSubreddit(this.data.subreddit, this.data.type, this.data.time, this.data.limit);

        return yield* gen;
    }
}
