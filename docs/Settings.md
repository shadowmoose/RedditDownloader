
# List of Settings
[Back to User Guide](./site/User_Guide.md)

Settings can be adjusted within the ```settings.json``` file RMD generates,
or they can be overridden by passing the setting category and name from the command line, like so:

```--category.setting_name``` 

*(For more information about command line options, see [Arguments.md](./Arguments.md))*

If a setting has options, its value **must** be one of its options.

**Note:** File output paths support tags to insert data about each post into the file path. 
See [the bottom of this page](#output-format) for more info.

**Below are the relevant categories, and their settings:**

## Auth
+ client_id
  + **Description:** *DEPRECATED* 
  + **Expected Type:** str 
  + **Default value:** [blank] 
+ client_secret
  + **Description:** *DEPRECATED* 
  + **Expected Type:** str 
  + **Default value:** [blank] 
+ password
  + **Description:** *DEPRECATED* 
  + **Expected Type:** str 
  + **Default value:** [blank] 
+ user_agent
  + **Description:** *The user agent to identify as, wherever possible.* 
  + **Expected Type:** str 
  + **Default value:** [Unique ID] 
+ username
  + **Description:** *DEPRECATED* 
  + **Expected Type:** str 
  + **Default value:** [blank] 
## Output
+ base_dir
  + **Description:** *The base directory to save to. Cannot contain tags.* 
  + **Expected Type:** str 
  + **Default value:** ./download/ 
+ subdir_pattern
  + **Description:** *The directory path, within the base_dir, to save files to. Supports tags.* 
  + **Expected Type:** str 
  + **Default value:** /[subreddit]/ 
+ file_name_pattern
  + **Description:** *The ouput file name. Supports tags.* 
  + **Expected Type:** str 
  + **Default value:** [title] - ([author]) 
+ deduplicate_files
  + **Description:** *Remove downloaded files if another copy already exists. Also compares images for visual similarity.* 
  + **Expected Type:** bool 
  + **Default value:** True 
## Threading
+ max_handler_threads
  + **Description:** *How many threads can download media at once.* 
  + **Expected Type:** int 
  + **Default value:** 5 
+ display_clear_screen
  + **Description:** *If it's okay to clear the terminal while running.* 
  + **Expected Type:** bool 
  + **Default value:** True 
+ display_refresh_rate
  + **Description:** *How often the UI should update progress, in seconds.* 
  + **Expected Type:** int 
  + **Default value:** 5 
## Interface
+ start_server
  + **Description:** *If the WebUI should be available.* 
  + **Expected Type:** bool 
  + **Default value:** True 
+ browser
  + **Description:** *Browser to auto-open UI in.* 
  + **Expected Type:** str 
  + **Default value:** chrome-app 
  + **Options:** 
    + chrome-app - *Chrome Application Mode (recommended)* 
    + default browser - *The default system browser* 
    + off - *Don't auto-open a browser* 
+ keep_open
  + **Description:** *If True, the WebUI will stay available after the browser closes.* 
  + **Expected Type:** bool 
  + **Default value:** False 
+ port
  + **Description:** *The port to open the WebUI on.* 
  + **Expected Type:** int 
  + **Default value:** 7505 
+ host
  + **Description:** *The host to bind on.* 
  + **Expected Type:** str 
  + **Default value:** localhost 


## Output Format:

The patterns allow for data insertion, based off the currently-processing post.

To insert them, include *'[tag_name]'* in the path. EG: *'/custom/[subreddit]/[user]/'*

**Available tags:** ```type``` *(will be 'Post'/'Comment')*, ```id```, ```title```, ```author```, ```subreddit```, ```source_alias```

__Files are saved as:__ *base_dir/subdir_pattern/file_pattern*

+ **base_dir**  - override base directory. This changes where the files are saved, and can be absolute or relative. Cannot contain inserted data.

+ **file_pattern** - override filename output pattern. *Do not include a file extension.*
  + URLs pointing to albums or groups of multiple files will save file_pattern as a directory, containing the incrementally-named files.
  
+ **subdir_pattern** - override subdirectory name pattern. 
  + Supports the same tags as *file_pattern*, but should always end with a path separator slash.