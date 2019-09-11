# What is a Filter?
*Filters are, as the name implies, tiny bits of logic
 you can add to any Sources to filter out any posts you might not want. They allow you to choose from all manner of
 ways to screen posts - such as Upvotes, Title, Body Text, SFW Warnings, Date Posted, etc.*

## Getting started with Filters
*Filters can be added/removed from a Source simply, using the WebUI.*

Filters are simple logic. They require 3 things:

+ A field to check from each post. (Upvotes, Title, Time Posted, etc)
+ A comparator value. (Minimum, Maximum, Equal to, or Regex Match)
  + "Regex Match", while more advanced, is very powerful. It allows you to filter by text values in creative ways.
+ The value to compare against. This is whatever you want the limit to be.


## Note: Filter Comparisons Logic
With Filter comparisons, numeric comparison (for "min"/"max") is only done if both values can be converted to numbers.

Make sure the comparators you're using make sense for the values they're compared against, 
or you may have unexpected results.

