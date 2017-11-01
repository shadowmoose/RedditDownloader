# Reddit Media Downloader [![Build Status](https://travis-ci.org/shadowmoose/RedditDownloader.svg?branch=master)](https://travis-ci.org/shadowmoose/RedditDownloader)


Scans all Upvoted &amp; Saved posts on your Reddit acount, searching for any media they link to. If it is able to, it then downloads that media. 

It works on most video sites, image hosts, and image blogs.
It also works with links inside comments, and links within selfpost text.

This program is useful for building archives of all the images and videos you've Upvoted or Saved over the years.

Avoids downloading duplicates of the same file, and will automatically seek to - and resume - where it last left off.


# Requirements:
1. **Python**: You can download Python executable for your operating system from [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Requires that you register an app at [Reddit's App Page](https://www.reddit.com/prefs/apps) to get access to view Posts through the Reddit API. Fortunately, they make this part extremely easy. Simply click to register a "Script" for personal use, name it whatever you want, and enter anything (like 'http://localhost' - it doesn't matter) for the URI/URL fields. You'll enter the client info it gives you into the settings file in the steps below.

*The program will launch an assistant to help you with the second requirement*, when run for the first time, but it doesn't hurt to get the client information prepared.

# Setup:
1. **Get the above requirements set up**
2. **Download:** Download this program, either using git or by [clicking here](../../releases/latest) *(Latest Release)*. If you download the zip, unpack it.
3. **Install dependencies:** launch a terminal inside wherever you saved the program, and run the line:

```
pip install -r requirements.txt
```
or
```
python main.py --update
```
4. Once the install finishes, launch the program with:
```
python main.py
```
On first launch, it will generate a *settings.json* file, where you can enter your data.

5. Whenever desired, you can automatically update the program and its dependencies by running:
```
python main.py --update
```

See [Here](Argument_Guide.md) for more information on (optional) parameters.

If you're checking this out with Git, I strongly suggest you pull the *latest release*, to assure stability.

# Issues?
This program uses multiple Handlers, included in the *handlers* directory, to process the various links it finds. Many are extremely generic to allow for the widest possible site coverage.
If you hit any links which it does not support, find anything broken, or just need assistance, please open a new request [here](../../issues/new).

*NOTE: This program is currently in an extremely tentative state, and functionality may radically change and expand in the future.*

# Supported Python Versions:
You should be fine with 3.4 up, and maybe even slightly earlier, but you can view the only versions I officially support at [The Travis Build Page](https://travis-ci.org/shadowmoose/RedditDownloader). It automatically checks the most recent commit, and runs through a strict set of tests to make sure nothing's broken.
