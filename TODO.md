# Stuff to Do Before Release
*  Make Sources check with Filters
*  Build genie for adding sources and filters.
*  Write testing for Sources and Filters
*  Build more Sources


*  Verify settings forward-compatibility from scratch.
*  Change how settings/context is passed down 
    * Expose Source alias to filename patterns
      * Possibly just append that data to the RedditElement
    * Possibly reevaluate how settings are handed off
      * Mostly to remove auth info from global scope. 