# Release 2.0
This major release brings threaded downloading.

RMD is now capable of concurrently downloading media files, massively shortening total run time.

### Changelog

+ Fix for multiple filename-related bugs
  + This includes auto-shortening of long paths for Windows. This fixes #19, and closes #20.
  + Also should properly handle edge-cases.
+ Patched a few mild, situational logical errors.
+ Adjusted the Wizard to react more intelligently.
+ The output during runtime now refreshes to better track thread progress.
  + The printout will attempt to dynamically resize to fit supported consoles. *(beta)*
  + Non-refreshing functionality - similar to the original - can be enabled in the settings.

**Note:** For anybody having issues with renaming/deleting files created on certain Windows platforms, 
a tool has been included (in */classes/tools/win_file_fixer*) to automatically repair these files. 
I've made sure to sanitize all filenames so similar bugs can't happen in the future.
