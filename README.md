# Reddit Media Downloader
**Master** [![Build Status](https://travis-ci.org/shadowmoose/RedditDownloader.svg?branch=master)](https://travis-ci.org/shadowmoose/RedditDownloader)

**Latest Release** [![Build Status](https://travis-ci.org/shadowmoose/RedditDownloader.svg?branch=latest-release)](https://travis-ci.org/shadowmoose/RedditDownloader/branches)

Scans all Upvoted &amp; Saved posts on your Reddit acount, searching for any media they link to. If it is able to, it then downloads that media. 

It works on most video sites, image hosts, and image blogs.
It also works with links inside comments, and links within selfpost text.

This program is useful for building archives of all the images and videos you've Upvoted or Saved over the years.

Avoids downloading duplicates of the same file, and will automatically seek to - and resume - where it last left off.


# Requirements:
1. **Python**: You can download Python executable for your operating system from [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Requires that you register an app at [Reddit's App Page](https://www.reddit.com/prefs/apps) to get access to view Posts through the Reddit API.

# Setup:
1. **Get the above requirements set up**
2. **Download:** Download this program, either using git or by [clicking here](../../archive/latest-release.zip) *(Latest Release)*. If you download the zip, unpack it.
3. **Install dependencies:** launch a terminal inside wherever you saved the program, and run the code:

```
pip install -r requirements.txt
```
4. Once the install finishes, launch the program with:
```
python reddit.py
```
On first launch, it will generate a *settings.json* file, where you can enter your data.

See [Here](Argument_Guide.md) for more information on (optional) parameters.

If you're checking this out with Git, I strongly suggest you pull from the *latest-release* branch, to assure stability.

# Issues?
This program uses multiple Handlers, included in the *handlers* directory, to process the various links it finds. Many are extremely generic to allow for the widest possible site coverage.
If you hit any links at the end which it does not support, feel free to request modules for them here.

*This program is currently in an extremely tentative state, and functionality may radically change and expand in the future.*

# Supported Python Versions:
You should be fine with 3.4 up, and maybe even slightly earlier, but you can view the only versions I officially support at [The Travis Build Page](https://travis-ci.org/shadowmoose/RedditDownloader). It automatically checks the most recent commit, and runs through a strict set of tests to make sure nothing's broken.
