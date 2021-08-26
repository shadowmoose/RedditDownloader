

export const ExampleTagObject = {
    id: 't3_1m12dk',
    title: 'Example Post Title',
    author: 'theshadowmoose',
    subreddit: 'test_sub',
    score: 1337,
    createdDate: '2021-01-22',
    nsfw: 'sfw',

    type: 'submission'
};

export type TemplateTags = typeof ExampleTagObject;

export const AvailableTemplateTags = Object.keys(ExampleTagObject);
