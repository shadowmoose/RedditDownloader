import {SubredditSorts, TimeRange} from "../source-interfaces";

export default interface SubredditPostsSchema {
    subreddit: string,
    sort: SubredditSorts,
    time: TimeRange,
    limit: number
}
