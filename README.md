[![Build Status](https://travis-ci.org/shadowmoose/RedditDownloader.svg?branch=master)](https://travis-ci.org/shadowmoose/RedditDownloader)

# Reddit Downloader
Scans all Upvoted &amp; Saved posts on your Reddit acount, looking for any external URLs they reference. If it is able to, it then downloads the content of those links.
It also attempts to parse links contained within comments or self-post text.

This program is useful for building archives of images and videos you've Upvoted or Saved over the years.

Avoids downloading duplicates of the same file, and will automatically scan to - and resume - where it last left off.

Requires that you register an app at [Reddit's App Page](https://www.reddit.com/prefs/apps) to get access to view Posts through the Reddit API.

On first launch, it will generate a *settings.json* file, where you can enter your data.

This program uses multiple Handlers, included in the *handlers* directory, to process the various links it finds. Many are extremely generic to allow for the widest possible site coverage.
If you hit any links at the end which it does not support, feel free to request modules for them here.

*This program is currently in an extremely tentative state, and functionality may radically change and expand in the future.*