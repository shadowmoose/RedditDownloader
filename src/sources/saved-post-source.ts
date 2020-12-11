import Source from "./source";
import * as reddit from '../reddit/snoo';
import {TypeOpts} from "../shared/source-interfaces";
import DBComment from "../database/entities/db-comment";
import {filterMap} from "../util/generator-util";

export default class SavedPostSource extends Source {
    protected data: any;
    readonly schema = {
        getComments: {
            description: 'Should RMD download saved comments?',
            type: TypeOpts.BOOLEAN,
            default: false
        }
    };
    readonly description: string = `The posts you've saved`;
    readonly type: string = 'saved-posts';

    async *find() {
        const gen = reddit.getSavedPosts();

        return yield* filterMap(gen, ele => {
            if (!(ele instanceof DBComment) || this.data.getComments) {
                return ele
            }
        })
    }
}
