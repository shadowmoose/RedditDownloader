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
This is automatically set in the WebUI, by requesting authorization from Reddit.

### Interface
The settings in this group all control how RMD handles displaying itself. 
By default, RMD will use a Web-based interface. if you would prefer to use a console-based interface, change these settings.

### base_dir
This is the base directory RMD will save all your files to. For best results, use an absolute path.

### file_name_pattern
This is the pattern RMD will use, within the base directory, to name the downloaded files. It supports folders, and should be relative.

This is a *pattern*, which means it can inject tagged data from each Post into the filename.
See [File Name Patterns](#file-name-patterns) for how to use this feature.

### concurrent_downloads
This controls how many concurrent downloads are allowed. Adjust this to control RMD's speed and resource usage.

### deduplicate_files
If enabled, RMD will delete any files - after downloading them - if it discovers a copy of the same file already exists.

Additionally, for images, RMD will perform a visual comparison between all images it downloads, 
and will remove images that are visually the same. This enables RMD to ignore lower-quality, compressed duplicates of the same pictures.

On the WebUI Browser side, RMD will remember which images have been deduplicated, and all unique posts will still be searchable.

---

## File Name Patterns
Anywhere File Patterns are used, they allow for data insertion based off the Post being saved.

To insert them, include *'[tag_name]'* in the path. EG: *'/custom/[subreddit]/[author]/'*

**Available tags:** ```type``` *(will be 'Post'/'Comment')*, ```id```, ```title```, ```author```, ```subreddit```, ```source_alias```

For example, you could tell RMD to output Posts to subdirectories based off Username by setting the pattern to 
something like `/[author]/[type]/[subreddit]/[title]`.

---

## Arguments in RMD
While it's suggested you make any settings changes with the WebUI, or in the 'settings.json' file generated, 
you may find yourself instead wanting to pass a few things in for one-off runs (or automation).

All arguments are optional:

**-h, --help** -        show help message and exit

**--settings** -        path to custom Settings file.

**--run_tests** -       launch in Test Mode. This will only work in testing environments.

**--category.setting** -  See [Changing Settings](#changing-settings) for usage.

**list_settings** - Print a list of all Settings, their descriptions, and their default values. Exits after printing.

**--source, -s** - Regex pattern. If specified, only sources - loaded from the settings file - with aliases matching a supplied pattern 
will be checked. This argument can be passed multiple times, to specify multiple patterns. 
*(EX: "main.py -s filter1 -s filter2 ...etc")*

**--version, -v** - Print the current RMD version, then exit.

**--limit** - See [Direct Downloading](#direct-downloading) for this usage.

---

## Direct Downloading
If you would like to, you can directly download from Users or Subreddits using only the command line, 
without a configured Source.

To do this, simply call RMD with the desired usernames or subreddits - including the `u/` or `r/` prefixes - separated by spaces.

When you use this feature, you may also specify a limit to the amount of Posts to be loaded. 
Do this by passing the `--limit` flag. if this is not specified, the default limit is 1000.

**EG:** `python redditdownloader /u/theshadowmoose r/funny --limit=500`

Calling RMD like this will disable any other preconfigured Sources for this run, and RMD will use the Terminal to display progress.
