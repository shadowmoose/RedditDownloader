import Source from "./source";
import * as reddit from '../reddit/snoo';
import {TypeOpts} from "../../shared/source-interfaces";

export default class UpvotedPostSource extends Source {
    protected data: any;
    readonly schema = {
        limit: {
            description: 'Maximum amount of posts:',
            type: TypeOpts.NUMBER,
            default: 0
        }
    };
    readonly description: string = `The submissions you've upvoted`;
    readonly type: string = 'upvoted-posts';

    async *find() {
        const gen = reddit.getUpvoted(this.data.limit);

        return yield* gen;
    }
}
