This major release brings threaded downloading.

RMD is now capable of concurrently downloading media files, massively shortening total run time.

Full changelog:

+ Fix for multiple filename-related bugs
  + This includes auto-shortening of long paths for Windows
  + Also should properly handle edge-cases.
+ Patched a few mild, situational logical errors.
+ Adjusted the Wizard to react more intelligently.
+ The output during runtime now refreshes to better track thread progress.
  + The printout will attempt to dynamically resize to fit supported consoles. (beta)
  + Similar, non-refreshing functionality to the original can be enabled in the settings.
