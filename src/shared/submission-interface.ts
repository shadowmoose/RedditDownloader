
export interface SubmissionInterface {
    title: string;
    author: string;
    subreddit: string;
    selfText: string;
    score: number;
    isSelf: boolean;
    createdUTC: number;
    nsfw: boolean;
}
