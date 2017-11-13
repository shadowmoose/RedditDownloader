# Stuff to Do Before Release

Important:

*  Build genie for adding sources and filters.
*  Write testing for Sources and Filters
*  Build more Sources
   * User-curated Multireddits
     * Sort by new/etc
     * optional time filter
*  Make sure to chase down all the TODO tags.
*  Consider switching to a generator provider system for loading elements

Pre-Release:

* Verify settings forward-compatibility from scratch.
* Possibly reevaluate how settings are handed off
  * Mostly to remove auth info from global scope. 
* Swap coveralls image branch.