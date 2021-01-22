import SavedPostSource from "./saved-post-source";
import DBSource from "../database/entities/db-source";
import SubredditPostSource from "./subreddit-post-source";
import Source from "./source";

/**
 * A list of all Source implementations.
 */
export const availableSources: ()=>Source[] = () => [new SavedPostSource(), new SubredditPostSource()];

/**
 * Convert the given DBSource into a Source instance, which can run its type-specific functionality.
 * @param dbo
 */
export function makeSource(dbo: DBSource) {
    const sources = availableSources();

    for (const s of sources) {
        if (s.type === dbo.type) {
            return s.createFromDB(dbo);
        }
    }
    throw Error(`Unknown SB Source type: "${dbo.type}"!`);
}
