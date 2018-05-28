# List of Settings

Settings can be adjusted within the ```settings.json``` file RMD generates,
or they can be overridden by passing the relevant ```--category.setting_name``` from the command line.

*(For more information about command line options, see [Arguments.md](./Arguments.md))*

If a setting has options, its value **must** be one of its options.

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
  + **Default value:** RMD-Scanner-0.522730981342159 
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
  + **Description:** *The directory path, within the base_dir, to save files to.* 
  + **Expected Type:** str 
  + **Default value:** /[subreddit]/ 
+ file_name_pattern
  + **Description:** *The ouput file name.* 
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
  + **Description:** *How often the UI should update progress.* 
  + **Expected Type:** int 
  + **Default value:** 5 
## Interface
+ start_server
  + **Description:** *If the WebUI should be available.* 
  + **Expected Type:** bool 
  + **Default value:** True 
+ browser
  + **Description:** *Browser mode to auto-open UI in.* 
  + **Expected Type:** str 
  + **Default value:** chrome-app 
  + **Options:** 
    + chrome-app - *Chrome Application Mode* 
    + default browser - *The default system browser* 
    + off - *Don't auto-open a browser.* 
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
