export const searchableFieldsList = ['title', 'author', 'body', 'subreddit'] as const;
/** The various fields that are supported by the server when searching downloads. */
export type SearchableField = typeof searchableFieldsList[number] | 'id';
export interface SearchColumn {
    column: SearchableField,
    value: any
}

export interface SearchCommand {
    where: SearchColumn[];
    limit: number;
    offset: number;
    order: SearchableField;
    ascending?: boolean;

    /** If true, all given `where` clauses must match for every returned post. */
    matchAll?: boolean;
}

export interface SearchFileInfo {
    id: string;
    type: string;
}

export interface DownloadSearchResult {
    submissionId: string;
    id: string;
    /** The ID of the retreived Download object. Should be unique among these query results. */
    dlUID: number;
    title: string;
    type: string;
    author: string;
    postType: 'comment'|'submission';
    postText: string;
    subreddit: string;
    isAlbumParent: boolean;

    albumID?: string;
    albumFiles?: {
        count: number;
        firstFile: SearchFileInfo
    }
}

export interface DownloadSearchResponse {
    count: number;
    downloads: DownloadSearchResult[];
}

export interface ParsedMediaMetadata {
    duration: number | null;
    bitrate: number | null;
    width: number | null;
    height: number | null;
    videoCodec: string | null;
    audioCodec: string | null;
    originalMediaTitle: string | null;
}


export interface AlbumFileDetails {
    id: number;
    mimeType: string;
}
