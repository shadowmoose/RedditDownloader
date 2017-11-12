# Stuff to Do Before Release

Important:

*  Filter values are currently case-sensetive, which should probably change.
   * This can be fixed by type-checking in filter.check()
     * only accept #s for >/<, and then lowercase() for == comparisons if both are strings.
*  Build genie for adding sources and filters.
*  Write testing for Sources and Filters
*  Build more Sources
*  Make sure to chase down all the TODO tags.
*  Consider switching to a generator provider system for loading elements

Pre-Release:

* Verify settings forward-compatibility from scratch.
* Possibly reevaluate how settings are handed off
  * Mostly to remove auth info from global scope. 
* Swap coveralls image branch.