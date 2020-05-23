# Release 3.1.0

__New sources & Minor Bug fixes__

RMD Update 3.1.0 brings a few new features with it. 

### Changelog

+ Two new Settings have been addeded:
  + *(output.manifest)* - allows you to customize the exact path to your manifest file.
  + *(processing.retry_failed)* - lets you skip retrying previously-failed downloads.
+ Several [command-line improvements](../Advanced_Usage/Settings.md) have been made:
  + RMD now supports directly passing reddit Submission/Comment URLs from the command line. 
  + RMD now supports [importing from a CSV file](../Advanced_Usage/Settings.md#importing-from-reddit-csv-export).
+ The oAuth flow in the UI has been improved, to support non-standard host configurations.
+ The "best" value has been removed from submission sorting options, as it is unsupported by the Reddit API.
+ Other minor bug fixes have been added across the program.
