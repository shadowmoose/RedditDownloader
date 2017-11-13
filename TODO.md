# Stuff to Do Before Release

Important:

*  Build genie for adding sources and filters.
*  Write testing for Sources and Filters
*  Build more Sources
   * Subreddit Posts
     * Sort by new/etc
     * optional time filter
   * Multireddit Posts
     * Same as above
   * User's Post/Comment history
*  Make sure to chase down all the TODO tags.
*  Consider switching to a generator provider system for loading elements

Pre-Release:

* Verify settings forward-compatibility from scratch.
* Possibly reevaluate how settings are handed off
  * Mostly to remove auth info from global scope. 
* Swap coveralls image branch.