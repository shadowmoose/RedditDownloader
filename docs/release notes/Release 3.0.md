# Release 3.0 - Bugfixes, SQLite, and a User Interface!

*Yes, I know I'm jumping a whole major version again.
Before I get into further detail, the major jump is because this release may bring breaking changes to some users.
The worst case is that RMD may re-download some posts it had already saved.
If you're an previous user with a *lot* of Posts saved, or you've been running RMD in automated server-side setups,
please read the patch notes before updating.*

## Full Changes:
__SQLite Manifest__
- The manifest (and all other non-setting data) is now stored in a SQLite database.
  + This massively shrinks the memory requirements for users downloading thousands of Posts.
  + Startup speed, as well as overall runtime, will likely be noticably faster for users.
  
- File hashes (used for deduplication) are now archived and timestamped.
  + This will prevent files from being re-hashed unless RMD finds one that has been modified since it last checked.
  + Being able to skip checking known files means RMD is massively faster when checking old Posts.
  
- File paths are now stored relative to the base download directory.
  + RMD can now be booted from anywhere (provided you tell it where the settings file is)
  + Moving the RMD base storage directory will no longer impact RMD's performance.
  
__User Interface (WebUI)__
- RMD now has a User Interface!
  + It's beaufiful.
  + it's browser-based.
  + It's also enabled by default after converting, so be sure to disable it if you're running on a headless server.

__Settings (and Command Line Argument) Overhaul__
- Settings have been rebuild from the ground up to provide much-neede features for supporting a UI.
  + Your old settings file will be automatically converted on the first post-update RMD launch.
    + Settings are still stored in ```settings.json```, and most of them are the same.
  + Several new settings have been added, relating the to WebUI.
- As a result of the Settings changes, there have been several added and removed command-line parameters.
  + Most notably, all parameters relating to things controlled by settings are now passed in a new format. (link here)

__Ding Dong, the Wizard's Dead__
- Because the UI is just so much better at managing Settings, the wizard has been replaced by it.
- Users running on external servers can either access the UI remotely, or run an RMD instance locally to generate the settings file.

__More Reddit Options__
- RMD can now sort all applicable Sources by "best".
- The *User Upvoted/Saved* Source now optionally accepts a list of Subreddits to individually scan.
  + For Reddit Gold members, specifying subreddits effectively increases the amount of posts RMD can find.

__Bug Fixes:__
- Comments now properly set their own ID, rather than their parent ID.
  + This requires a one-time conversion, which will attempt to prevent RMD from re-downloading those Posts.
    + The conversion will automatically run the first time you launch RMD post-update.
  + While most Comments will likely be converted, if you've got an especially large amount of comments already saved, you may notice several end up downloading duplicates.
  + If you're still concerned, [see here](https://github.com/shadowmoose/RedditDownloader/issues/31#issuecomment-395538681) for more information.
- Long filenames on non-windows systems should be properly trimmed to OS length constraints.
- Fixed a possible (but unlikely) race condition where the same Post could be processed twice when the stars aligned.
