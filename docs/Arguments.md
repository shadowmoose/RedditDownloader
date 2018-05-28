# List of arguments, in-depth:
While it's suggested you make any settings changes in the 'settings.json' file generated, 
you may find yourself instead wanting to pass a few things in for one-off runs (or automation).

All arguments are optional, but some must be supplied in a group (and are grouped as such):

**-h, --help** -        show help message and exit

**--settings** -        path to custom Settings file.

**--test** -            launch in Test Mode. Only used for TravisCI testing. 
*Will not operate outside of the testing environment.*

**--update | --update_only**   -         Attempt to update all program files and required packages, based off the latest RMD release.
This is convenience functionality built in for the sake of simple automation, or users not familiar with Python/Git.

Note: *On some systems, the process of updating Python packages will require Root/Administrator to work.*


**--skip_pauses** -     If supplied, skips any pauses for confirmation, by auto-accepting prompts. Useful for automation.

**--duplicate, -nd** - The program automatically removes duplicate files when it detects an existing copy from another 
Post. Pass this to disable that behavior. If CPU/RAM usage is an issue, disabling deduplication may help.

**--source, -s** - If specified, only sources - loaded from the settings file - with aliases matching a supplied pattern 
will be checked. This argument can be passed multiple times, to specify multiple patterns. 
*(EX: "main.py -s filter1 -s filter2 ...etc")*

## Setting overriding

You can override any of the [settings RMD uses](./Settings.md) by passing them as parameters. 

They should be passed in the format:
```--category_name.setting_name=new_value```

For a list of available settings, see [Settings.md](./Settings.md).