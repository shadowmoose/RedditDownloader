import {SubmissionInterface} from "./submission-interface";
import {CommentInterface} from "./comment-interface";

export default interface FilterInterface {
    id: number;
    forSubmissions: boolean;
    negativeMatch: boolean;
    field: string;
    comparator: ComparatorKeyTypes;
    valueJSON: string;
}

/**
 * A map of all viable Filter comparators, and their user-friendly display names.
 */
export const FilterComparators = {
    '>': 'greater than',
    '<': 'less than',
    '=': 'equal to',
    're': 'regex matching'
};
export type ComparatorKeyTypes = keyof typeof FilterComparators;
export type FilterComparator = (val1: any, val2: any) => boolean;
export const FilterComparatorFunctions: Record<ComparatorKeyTypes, FilterComparator> = {
    '>': (val1, val2) => {
        return val1 > val2
    },
    '<': (val1, val2) => {
        return val1 < val2
    },
    '=': (val1, val2) => {
        return val1 == val2
    },
    're': (val1, val2) => {
        return Boolean(`${val1}`.match(new RegExp(val2, 'gmi')))
    },
}

export type FilterPropTypes = 'string'|'number'|'boolean'|'datetime';
export interface FilterPropInfo {
    displayName: string;
    type: FilterPropTypes;
}

export const SubmissionFilters: Record<keyof SubmissionInterface, FilterPropInfo> = {
    author: {displayName: 'Author', type: 'string'},
    createdUTC: {displayName: 'Created Date', type: 'datetime'},
    isSelf: {displayName: 'Self Post', type: 'boolean'},
    over18: {displayName: 'Over 18', type: 'boolean'},
    score: {displayName: 'Score', type: 'number'},
    selfText: {displayName: 'Self Text', type: 'string'},
    subreddit: {displayName: 'Subreddit', type: 'string'},
    title: {displayName: 'Title', type: 'string'}
};

export const CommentFilters: Record<keyof CommentInterface, FilterPropInfo> = {
    author: {displayName: 'Author', type: 'string'},
    createdUTC: {displayName: 'Created Date', type: 'datetime'},
    score: {displayName: 'Score', type: 'number'},
    selfText: {displayName: 'Self Text', type: 'string'},
    subreddit: {displayName: 'Subreddit', type: 'string'},
};
