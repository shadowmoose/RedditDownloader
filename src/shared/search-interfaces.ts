
/** The various fields that are supported by the server when searching downloads. */
export type SearchableField = 'title'|'author'|'body';
export interface SearchColumn {
    column: SearchableField,
    value: any
}
