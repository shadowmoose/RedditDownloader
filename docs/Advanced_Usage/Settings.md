title: Settings & Arguments

# Settings & Arguments
There are many ways to customize Reddit Media Downloader to your liking, and this page attempts to document them.

## Changing Settings
Settings can be adjusted within the WebUI, the ```settings.json``` file RMD generates,
or they can be overridden by passing the setting category and name from the command line, like so:

```--category.setting_name``` 

If a setting has multiple options, its value **must** be one of its options.

To see all the possible settings, [check out the Settings List page.](Settings_List.md)

---

## Notable Settings
*There are a few settings that many people will specifically want to change, so they are documented here.*

### Auth
This is set using the WebUI, by requesting authorization from Reddit.

### Interface
The settings in this group all control how RMD handles displaying itself. 
By default, RMD will use a Web-based interface. if you would prefer to use a console-based interface, change these settings.

### base_dir
This is the base directory RMD will save all your files to. For best results, use an absolute path.

### file_name_pattern
This is the pattern RMD will use, within the base directory, to name the downloaded files. It supports folders, and should be relative.

This is a *pattern*, which means it can inject tagged data from each Post into the filename.
See [File Name Patterns](#file-name-patterns) for how to use this feature.

### manifest
This is the path to the database file that RMD creates to track download progress.
If this setting is a relative path (starting with "./"), it is relative to the download directory. 
RMD also allows this to be an absolute path (typically something like "C://", depending on your system).

If you wish to download to a directory on a network/remote drive you *must* change this to a local path,
because RMD requires the ability to exclusively access this file - which most networks will not allow.

### concurrent_downloads
This controls how many concurrent downloads are allowed. Adjust this to control RMD's speed and resource usage.

### deduplicate_files
If enabled, RMD will delete any files - after downloading them - if it discovers a copy of the same file already exists.

Additionally, for images, RMD will perform a visual comparison between all images it downloads, 
and will remove images that are visually the same. This enables RMD to ignore lower-quality, compressed duplicates of the same pictures.

On the WebUI Browser side, RMD will remember which images have been deduplicated, and all unique posts will still be searchable.

### Imgur Settings
Imgur is a major media host on Reddit. 
For direct imgur links, or links to public albums, RMD will work just fine without configuring these settings.
Some imgur albums, however, are hidden from the public view.

In order to support hidden/private albums or galleries, 
you'll need to [register an imgur application](https://api.imgur.com/oauth2/addclient) and provide the ID & Secret to RMD.

[The imgur API has limits.](https://api.imgur.com/#limits)
RMD will try as hard as it can to avoid using the API, 
but it will use the API if it encounters a private album/gallery that it otherwise cannot scrape.
Links to single images will not use the API.

*If you do not want to use the imgur API, and are okay with some albums failing, you can leave these settings blank.*

**To register an imgur Application:**

+ Visit [https://api.imgur.com/oauth2/addclient](http://api.imgur.com/oauth2/addclient) while signed in to imgur.
+ On the registration page, the Name/Callback URL/Website/Description can be any values. 
+ Check the box for "Anonymous usage without user authorization"
+ Fill in a valid email address
+ Click submit, then copy the Client ID & Secret from the following page.

---

## File Name Patterns
Anywhere File Patterns are used, they allow for data insertion based off the Post being saved.

To insert them, include *'[tag_name]'* in the path. EG: *'/custom/[subreddit]/[author]/'*

**Available tags:** 

+ ```type``` *(will be 'Post'/'Comment')*
+ ```reddit_id```
+ ```title```
+ ```author``` 
+ ```subreddit```
+ ```source_alias```
+ ```created_utc``` *(A numeric Unix Timestamp, eg: 1552739416)*
+ ```[created_date]``` *(Formatted as 'YYYY-MM-DD')*
+ ```[created_time]```*(Formatted as 'HH.MM.SS')*

For example, you could tell RMD to output Posts to subdirectories based off Username by setting the pattern to 
something like `/[author]/[type]/[subreddit]/[created_date] [created_time] - [title]`.

The above pattern would generate a file path similar to 
```/ShadowMoose/Submission/DataHoarder/2019-10-21 02.20.15 - Test Post.jpg``` for each file downloaded.

---

## Arguments in RMD
While it's suggested you make any settings changes with the WebUI, or in the 'settings.json' file generated, 
you may find yourself instead wanting to pass a few things in for one-off runs (or automation).

All arguments are optional:

**-h, --help** -        show help message and exit

**--settings** -        path to custom Settings file.

**--run_tests** -       launch in Test Mode. This will only work in testing environments.

**--category.setting** -  See [Changing Settings](#changing-settings) for usage.

**--list_settings** - Print a list of all Settings, their descriptions, and their default values. Exits after printing.

**--source, -s** - Regex pattern. If specified, only sources - loaded from the settings file - with aliases matching a supplied pattern 
will be checked. This argument can be passed multiple times, to specify multiple patterns. 
*(EX: "main.py -s filter1 -s filter2 ...etc")*

**--version, -v** - Print the current RMD version, then exit.

**--authorize, -a** - Manually use the in-console authentication method to grant RMD access to Reddit.

**--limit** - See [Direct Downloading](#direct-downloading) for this usage.

**--import_csv** - See [Importing from Reddit CSV Export](#importing-from-reddit-csv-export) for this usage.

**--full_csv** - See [Importing from Reddit CSV Export](#importing-from-reddit-csv-export) for this usage.

---

## Direct Downloading
If you would like to, you can directly download from Users or Subreddits using only the command line, 
without a configured Source.

To do this, simply call RMD with the desired usernames or subreddits - including the `u/` or `r/` prefixes - separated by spaces.

When you use this feature, you may also specify a limit to the amount of Posts to be loaded. 
Do this by passing the `--limit` flag. if this is not specified, the default limit is 1000.

You may also pass a full, direct permalink to a reddit Comment or Submission.

*Download Moose's Comments+Submissions, and Submissions from Funny, limiting both to the first 1000:*

+ `python redditdownloader /u/theshadowmoose r/funny --limit=500`

*Download a single Submission:*

+ `python redditdownloader https://www.reddit.com/r/shadow_test_sub/comments/gf2n8i/` 

Calling RMD like this will disable any other preconfigured Sources for this run, and RMD will use the Terminal to display progress.


## Importing from Reddit CSV Export
RMD allows you to input a CSV file to download the Posts inside. 
You can request a full user file [from Reddit's data-request web page](https://www.reddit.com/settings/data-request).

Reddit limits your Upvoted/Saved history to the most recent 1000 results. 
However, if you request the data files for your account, they will provide you with - 
among other data - `comment_votes.csv` & `post_votes.csv` files.

These two files can be fed into RMD to download your entire account's history. Simply call RMD like so:

+ `python redditdownloader --import_csv="path/to/file.csv" [--full_csv]`

For speed reasons, RMD attempts to use *only* PushShift to find historic post data by default. 
Submissions and Comments that are old enough may be too old to exist in this database. 
If you want RMD to still try to find these, include the `--full_csv` flag.
This will be limited to Reddit's rate limiting per-lookup, and thus will be very slow whenever it has to check for a missed post.
