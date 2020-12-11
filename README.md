_This is the WIP branch for converting RMD into TypeScript. At any given moment, the code within may or may not be operational._

# Reddit Media Downloader 
[![badge](https://github.com/shadowmoose/RedditDownloader/workflows/Pytest/badge.svg)](https://github.com/shadowmoose/RedditDownloader/actions) 
[![badge](https://github.com/shadowmoose/RedditDownloader/workflows/Docs/badge.svg)](https://shadowmoose.github.io/RedditDownloader/)
[![Docker Build](https://img.shields.io/docker/cloud/build/shadowmoose/redditdownloader)](https://hub.docker.com/r/shadowmoose/redditdownloader)
[![codecov](https://codecov.io/gh/shadowmoose/RedditDownloader/branch/master/graph/badge.svg)](https://codecov.io/gh/shadowmoose/RedditDownloader)
![lines of code](https://raw.githubusercontent.com/shadowmoose/RedditDownloader/project-badges/loc-badge.svg)

**Let's face it:** In this day and age, the internet is ephemeral. Anything anybody posts might be here one day,
and gone the next. Websites take down or move their images and videos, posts get hidden or removed, and their
content is lost. Even more so on Reddit, where accounts are constantly springing into existence -
and then vanishing as quickly without a trace. How's anybody supposed to keep their cherished cat picture 
collection around with all this change? Well fear not, my data-hoarding friend,
because Reddit Media Downloader is here for you!

![RMD Preview Image](https://thumbs.gfycat.com/UniqueBigFinnishspitz-size_restricted.gif)


# What is this?
**Reddit Media Downloader** is a program built to scan Comments & Submissions from multiple sources on Reddit, 
and download any media they contain or link to. It can handle scanning posts from your personal 
Upvoted/Saved lists, subreddits of your choice, user-curated multireddits, and more!
When it finds a Comment or Submission from wherever you specify, it will parse the text and links within to
find any media linked to. It then uses multiple downloaders to save this media locally onto your disk.


**RMD** comes equipped with a suite of options to let it scan just about anywhere you can find media on Reddit.
Coupled with its powerful baked-in Filter options to let you specify exactly what type of posts and comments
you're looking for (*"I only want Submissions with 'Unicorn' in the title, and no less than 1000 upvotes!"*), 
RMD makes automatically saving things a simple process. Built in Python and runnable headless (without a GUI) or as its own server, 
you can launch this program anywhere - and it's built from the ground-up to make automation a breeze.

[Check out the different places RMD can scan!](https://shadowmoose.github.io/RedditDownloader/Getting_Started/Sources/#list-of-supported-sources)

# Things RMD Can Do:
* Extract links inside comments, links in Submissions, and links within selfpost text.
* Work with links to most video sites, image hosts, and image blogs.
* Avoid saving duplicates of the same file, by using image recognition to compare similar pictures.
* Automatically seek to - and resume - where it last left off downloading.
* Launch a web-based UI (locally or remotely) to make even the most complex configuration setups simple.

# Getting Started:
[Click here to visit the documentation site!](https://shadowmoose.github.io/RedditDownloader/)


# New Feature Requests or Issues?
If you hit any links which RMD does not support, find anything broken, need assistance, or just want to suggest new features, please open a new request [here](https://github.com/shadowmoose/RedditDownloader/issues/new/choose).
