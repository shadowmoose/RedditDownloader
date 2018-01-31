# List of arguments, in-depth:
While it's suggested you make any settings changes in the 'settings.json' file generated, 
you may find yourself instead wanting to pass a few things in for one-off runs (or automation).

All arguments are optional, but some must be supplied in a group (and are grouped as such):

**-h, --help** -        show help message and exit

**--wizard, -w** - Launch the visual Setup Wizard, to make changes to your Settings/Sources/Filters.

**--settings** -        path to custom Settings file.

**--test** -            launch in Test Mode. Only used for TravisCI testing. 
*Will not operate outside of the testing environment.*

**--update**  -         Attempt to update all program files and required packages, based off the latest RMD release.
This is convenience functionality built in for the sake of simple automation, or users not familiar with Python/Git.
*On some systems, the process of updating Python packages will require Root/Administrator to work.*

**--update_only** -     Same as *--update*, only the script will stop afterwords without scanning for posts. 
*See above note.*

**--skip_pauses** -     If supplied, skips any pauses for confirmation, by auto-accepting prompts. Useful for automation.

**--duplicate, -nd** - The program automatically removes duplicate files when it detects an existing copy from another 
Post. Pass this to disable that behavior. If CPU/RAM usage is an issue, disabling deduplication may help.

**--skip_manifest** - The Manifest generated is used to rapidly skip files downloaded in previous runs. 
If you download a lot of shifting content, such as constantly-updated imgur albums, use this to ignore the manifest.

**--source, -s** - If specified, only sources - loaded from the settings file - with aliases matches a supplied pattern 
will be checked. This argument can be passed multiple times, to specify multiple patterns. 
*(EX: "main.py -s filter1 -s filter2 ...etc")*

#### Pass login parameters through arguments:
(All are required to be passed at once)
+ **--username**  -       account username. 

+ **--password**  -       account password.

+ **--c_id**   -          Reddit client id.  *You must register an app on Reddit to use this. See README.*

+ **--c_secret**  -       Reddit client secret.  *See above note.*

+ **--agent**   -         String to use for User-Agent.  *A string that identifies your client to Reddit. 
This can be whatever you want.*

#### Output Format:
The patterns aren't required, but changing either requires that you first also supply the **base_dir** parameter.

The patterns allow for data insertion, based off the currently-processing post.

To insert them, include *'[tag_name]'* in the path. EG: *'/custom/[subreddit]/[user]/'*

**Available tags:** type *('Post'/'Comment')*, id, title, author, subreddit, source_alias

__Files are saved as:__ *base_dir/subdir_pattern/file_pattern*

+ **--base_dir**  -       override base directory. This changes where the files are saved, and can be absolute or relative.

+ **--file_pattern** -    override filename output pattern. *Leave extension out.*
  + URLs pointing to albums or groups of multiple files will save file_pattern as a directory, containing the incrementally-named files.
  
+ **--subdir_pattern** -  override subdirectory name pattern. 
  + Supports the same tags as *file_pattern*, but should always end with a path separator slash.
