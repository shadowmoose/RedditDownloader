title: FAQ & Common Issues


## Why does RMD only find 1000 results?
Though RMD can theoretically support any amount of results, Reddit limits most resources to the first 1000 results.
This means that most User/Subreddit/etc Sources will be limited to 1000 results, maximum.

The [PushShift Sources](Sources.md#pushshift-subreddit-submissions) do not have this problem, and are recommended if you need more than the 1000 post limit.


## Can I run this on a network drive?
RMD will not run well on any kind of remote file system. 
This technical reason for this is because the manifest file it uses to track download progress 
is an SQLite file, which requires the ability to be exclusively locked.

If you wish to download to a network directory, please look at storing the manifest locally on the system
by changing the `output.manifest` setting to a local absolute path.

## I have a bug or feature request.
+ I'm always open to bug reports or feature requests, so [hit me up](https://github.com/shadowmoose/RedditDownloader/issues/new/choose)!
