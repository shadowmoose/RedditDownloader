import FilterInterface from "./filter-interface";

export enum SourceTypes {
    SAVED_POSTS = 'saved-posts',
    UPVOTED_POSTS = 'upvoted-posts',
    SUBREDDIT_POSTS = 'subreddit-posts',
}


export interface SourceInterface {
    dataJSON: string
    id: number
    name: string
    type: SourceTypes
}


export interface SourceGroupInterface {
    name: string;
    id: number;
    color: string;
    filters: FilterInterface[];
    sources: SourceInterface[];
}

export const TimeRange = ['hour', 'day', 'week', 'month', 'year', 'all'];
export type TimeRange = 'hour' | 'day' | 'week' | 'month' | 'year' | 'all';
export const SubredditSorts = ['hot', 'new', 'top', 'rising'];
export type SubredditSorts = 'hot' | 'new' | 'top' | 'rising';
