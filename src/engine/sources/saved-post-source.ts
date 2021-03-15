import Source from "./source";
import * as reddit from '../reddit/snoo';
import {TypeOpts} from "../../shared/source-interfaces";
import DBComment from "../database/entities/db-comment";
import {filterMap} from "../util/generator-util";

export default class SavedPostSource extends Source {
    protected data: any;
    readonly schema = {
        getComments: {
            description: 'Should RMD download saved comments?',
            type: TypeOpts.BOOLEAN,
            default: false
        },
        limit: {
            description: 'Maximum amount of posts:',
            type: TypeOpts.NUMBER,
            default: 0
        }
    };
    readonly description: string = `The posts you've saved`;
    readonly type: string = 'saved-posts';

    async *find() {
        const gen = reddit.getSavedPosts(this.data.limit);

        return yield* filterMap(gen, ele => {
            if (this.data.getComments || !(ele instanceof DBComment)) {
                return ele
            }
        })
    }
}
