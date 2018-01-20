# Intro
So you've decided to give Reddit Media Downloader a try, eh? Great! 
Here are a few things you'll probably want to know.

Either read through this document or skip to the [Example](#example)

For information about the Arguments RMD accepts, check [Arguments.md](../Arguments.md)

### Setup:
[**The full setup guide can be found** here](./Setup_Requirements.md).

Once you've installed the requirements, you can launch RMD using the command:

```python main.py```

In a terminal opened inside the folder you've saved RMD to (the directory with "main.py").

*Windows Note: You can open a terminal in the folder by holding shift and right-clicking the folder (not the files inside it), then selecting "Open Window Here"*

The first time you run the program, you will be prompted to set details and (optionally)
launch a Wizard to simplify the process.

But before we dive into that, we should cover some terminology:

### Settings, Sources, & Filters:
In Reddit Media Downloader, every Comment and Submission (it calls them "Posts") comes from a *Source*.

As the name implies, a [*Source*](Supported_Sources.md) is simply wherever posts are being pulled from. A Source can be a subreddit,
your upvoted posts, a user's comment history, or more. RMD comes with quite a few options built in.

The bulk of the setup process for RMD involves simply choosing what Sources you'd like to download from.
Where possible, Sources have setup options to let you choose how you'd like to sort posts ("Hot", "Top", etc.),
what period of time you'd like to check posts from ("Last Hour", "Last Week", "All Time", etc.), 
and how many posts you'd like the Source to scan. You can have as many [Sources](Supported_Sources.md) as you want!

[Here's a list of the supported Source Types](Supported_Sources.md)

Standing on top of the Sources, RMD provides *Filters*. *Filters* are, as the name implies, tiny bits of logic
you can add to any Sources to filter out any posts you might not want. They allow you to choose from all manner of
ways to screen posts - such as Upvotes, Title Text, NSFW Warnings, Date Posted, etc.

*Sources* and *Filters* combine to make a potent combination. If you're more programatically-inclined, 
they can be written in simple JSON by hand. For the rest of us, there's a Wizard to walk you through it.

### The Wizard:
The Setup Wizard is a great tool to manage your Settings, Sources, & Filters.

Launched automatically on the first-time setup, it can be re-run to adjust Sources at any time by calling:

```python main.py -w```

The Wizard is a text-based interface to walk you through setting things up automagically.

You can use it to change your account information, or to add/edit/remove Sources (and their Filers).

Sources can be added from a list it will display, and are fairly straightforward to set up.

Filters can be added/removed from a Source by selecting "Edit a Source", and choosing the appropriate action
from the submenu it presents.

Filters are simple logic. They require 3 things:
+ A field to check from each post. (Upvotes, Title, Time Posted, etc)
+ A comparator value. (Minimum, Maximum, Equal to, or Regex Match)
  + "Regex Match", while more advanced, is very powerful. It allows you to filter by text values in creative ways.
+ The value to compare against. This is provided by you.

Still sound complicated? Don't worry - I'll provide an example setup to show how simple this really is.

### Example:
So, for instance, if I wanted to download the **top 100** images from all time in **/r/aww**:

1. First I'd go into the Wizard and select *'Add a new Source'*
2. I would then select *'The submissions in a given subreddit'* from the list provided.
3. When prompted, I'd enter 'awww' as the subreddit, and choose 'top' from the sort options when prompted.
4. I'd finish setting the Source up by entering '*100*' when prompted for the amount of Posts I'd like.
5. Finally I just need to name this filter when prompted, and choose something I'll recognise if I need to 
come back and make changes.

**The Source is now complete!**
I could now exit the Wizard and relaunch the program without the *'-w'* flag, and it would kick off downloading
my adorable animal picture archive.

...But what if I only want **kitten** pictures? Let's say I only want to scan the top 100, and pull any pictures
of adorable kittens from them. We need a way to only download posts with "kitten" in their title. 
*"How would I do that"*, you ask? It's time for a *Filter*!

1. First, I need to go back into the Wizard and select "Edit a source", then select the Source I just made.
2. Once selected, I choose "Add a Filter" from the prompt.
3. From the new list, I'll choose "title"
4. In the next prompt, I pick "match", to perform a more in-depth text check.
5. Finally, I'm going to enter the simple pattern of "kitten" to match against. 
6. Save and exit. When relaunched again, it will screen out any posts not matching my new Kitten Filter!

*(This could be a far more advanced pattern, but REGEX is outside the scope of this guide.)*

If I wanted to screen it further - say only accepting posts with at least 10,000 upvotes - I'd do the same process,
but select "score", "minimum", and enter *"10000"*. There are tons of options, and you can have as many Filters
as you want on any given Sources. Play around with it!


# Closing Notes:
There are a few things to take note of, if you're interested in the nitty-gritty.
+ "Unlimited" generally isn't a thing. Reddit limits most resources to the first 1000 results.
   + RMD will likely be limited to the first 1000 results for any given Source.
+ Due to Reddit API limitations, signing in to RMD is absolutely required.
+ For Filter comparisons, numeric comparison (for "min"/"max") is only done if both values can be converted to numbers.
+ I'm always open to bug reports or feature requests, so hit me up!