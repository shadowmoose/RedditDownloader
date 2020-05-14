title: Sources

# What is a Source?
_A "Source" is, simply, represents a place from Reddit where RMD should look for posts. 
You can individually configure Sources to pull Submissions or Comments from all over Reddit, 
including Subreddits, User Profiles, Multireddits, and your own Liked/Saved feed._

## Using Sources
By default, RMD will include a Source to find & download your personal Liked & Saved posts. 
This is the default behavior since RMD's release.

To change this in the WebUI, simply remove that source and add new ones. 
You can have as many as you'd like - including duplicates of the same Source type.

Most sources have some options to let you sort and filter the posts they find. 
If you'd like to filter them further, [add as many extra Filters](../Advanced_Usage/Filters.md) as you need. 
Filters are applied per-Source, to allow maximum customization.

You give each Source a unique name when you set them up, and - if you desire - this alias can be embedded into 
the final file output paths [(See "Output Format" in Settings.md)](../Advanced_Usage/Settings.md) to further differentiate 
the various sources.


---

## List of Supported Sources:

*This is a list of all supported Sources.*

#### Subreddit Submissions
+ Scan Submissions from the target subreddit.
+ As with many sources, supports sorting by "Hot/Top/Etc"
+ Also supports sorting by time. (Last Hour/Day/Month/All Time/Etc)
    
#### Your Reddit Front Page
+ Supports all standard methods of sorting.
+ Personalized to the authorized account.
+ This Source is added by default on setup, but can be removed.

#### Your Upvoted and/or Saved Submissions & Comments
+ Scan all the posts you've personally Upvoted or Saved.
+ For more flexible configuration, use the *User Upvoted/Saved* source.
+ For Comments, only comments you've Saved can be located.

#### User Upvoted/Saved Submissions & Comments
+ Allows you to choose a Username, and scan their Upvoted and/or Saved posts
+ This Source only works for Users who are set to Public, or for your authorized account.

#### User-curated MultiReddit
+ Great for tracking personal or public groups of subs.
+ Provide a username and multireddit name to use.

#### User's Submission & Comment History
+ Choose a username, and scan their full Submission and/or Comment History.

#### PushShift: Subreddit Submissions
+ Load Submissions from a Subreddit, from the [PushShift](https://pushshift.io/) database. 
+ This allows unlimited Posts to be found, and even (usually) includes submissions deleted from Reddit.

#### PushShift: User Submission & Comment History
+ Load Posts from a User's history, from the [PushShift](https://pushshift.io/) database.
+ This allows unlimited Posts to be found, and even (usually) includes Posts deleted from Reddit.

#### PushShift: Search Submissions
+ Search the [PushShift](https://pushshift.io/) database for Submissions matching the specified term.
+ Supports an (optional) list of Subreddits, which can limit the search. If not provided, searches all of Reddit.
+ This allows unlimited Posts to be found, and even (usually) includes Posts deleted from Reddit.


#### Posts & Submissions From Reddit Data-Request Files
+ Visit [https://www.reddit.com/settings/data-request](https://www.reddit.com/settings/data-request) to get your complete account history as CSV files.
+ [Pass these files into RMD](../Advanced_Usage/Settings.md#importing-from-reddit-csv-export) 
    to download everything you've ever liked, fixing typical Reddit limitations.
