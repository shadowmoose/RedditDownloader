# Release 3.0.0

__Bugfixes, SQLite, and a User Interface!__

_Yes, I know I'm jumping a whole major version again.
Before I get into further detail, the major jump is because this release may bring breaking changes to some preexisting users.
If you're a previous user with a *lot* of Posts saved, or you've been running RMD in automated server-side setups,
please read the patch notes before updating._

_See [Upgrading](#upgrading) at the bottom of this file, before running the upgraded RMD on an old database._


---

## SQLite Manifest
- The manifest (and all other non-setting data) is now stored in a SQLite database.
    + This massively shrinks the memory requirements for users downloading thousands of Posts.
    + Startup speed, as well as overall runtime, will likely be noticably faster for users.
  
- File hashes (used for deduplication) are now archived and timestamped.
    + This will prevent files from being re-hashed unless RMD finds one that has been modified since it last checked.
    + Being able to skip checking known files means RMD is massively faster when checking old Posts.
  
- File paths are now stored relative to the base download directory.
    + RMD can now be booted from anywhere (provided you tell it where the settings file is)
    + Moving the RMD base storage directory will no longer impact RMD's performance.
  
## User Interface (WebUI)
- RMD now has a User Interface!
    + It's has an awesome media viewer.
    + it's browser-based.
    + It's also enabled by default after converting, so be sure to disable it if you're running on a headless server.

## Settings (and Command Line Argument) Overhaul
- Settings have been rebuild from the ground up to provide much-needed features for supporting a UI.
    + Your old settings file will be automatically converted on the first post-update RMD launch.
      + Settings are still stored in ```settings.json```, and most of them are the same.
    + Several new settings have been added, relating the to WebUI.
- As a result of the Settings changes, there have been several added and removed command-line parameters.
    + Most notably, all parameters relating to things controlled by settings are now passed in a new format. [Check the new options here](../Advanced_Usage/Settings.md#arguments-in-rmd)

## Ding Dong, the Wizard's Dead
- Because the UI is just so much better at managing Settings, the wizard has been replaced by it.
- Users running on external servers can either access the UI remotely, or run an RMD instance locally to generate the settings file.

## New Authentication
+ RMD no longer accepts usernames and passwords for authentication. Instead, it uses oAuth.
    + Big thanks to the PRAW Devs for fixing [the oAuth bug](https://github.com/praw-dev/praw/issues/955) previously preventing this
    + This also enables accounts with 2FA to authorize smoothly.

## More Reddit Options
- RMD can now sort all applicable Sources by "best".
- Many Sources now optionally accept a list of comma-separated subreddits/users/etc to individually scan.

## PushShift Support
- PushShift has been added for scanning Subreddits and Users.
    + The PushShift API allows you to scan beyond the 1000 post limit Reddit's site has, and it's fast!

## Multiprocessing Support
- RMD now uses multiple processes, instead of multiple threads.
    + This allows RMD to use multiple CPU cores, and prevents bottlenecking during heavy downloading.

## Prebuilt Binaries & Automatic updater
- RMD releases now come with prebuilt binary executables - supporting Windows, MacOS, and Ubuntu.
- If you use one of these binaries, it will (by default) automatically update itself to the latest packages.
    + This auto-update feature makes sure that you're using the latest packages to download the broadest site support.
    + To disable this feature, either use the python version, or launch the binary with `--skip_update`.

## Bug Fixes
- Comments now properly set their own ID, rather than their parent ID.
    + This requires a one-time conversion, which will attempt to prevent RMD from re-downloading those Posts.
    + While most Comments will likely be converted, if you've got an especially large amount of comments already saved, you may notice several end up downloading duplicates.
    + If you're still concerned, [see here](https://github.com/shadowmoose/RedditDownloader/issues/31#issuecomment-395538681) for more information.
- Long filenames on non-windows systems should be properly trimmed to OS length constraints.
- Fixed a possible (but unlikely) race condition where the same Post could be processed twice when the stars aligned.

## Upgrading
Upgrading to this RMD version will require you to first run a conversion utility, which is bundled with RMD.

This tool can be launched, using ```python redditdownloader/tools/manifest_converter.py```. 
You can also directly launch it directly from within its folder.

The tool exists to convert old database formats to the new one, as well as fix a few data bugs from older versions. 
Because of these bugs, not all posts may be correctly migrated to the new format. These will be logged in a file inside the new output folder, for you to manually handle.
