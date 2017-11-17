# Reddit Media Downloader 
[![Build Status](https://travis-ci.org/shadowmoose/RedditDownloader.svg?branch=master)](https://travis-ci.org/shadowmoose/RedditDownloader) [![Coverage Status](https://coveralls.io/repos/github/shadowmoose/RedditDownloader/badge.svg?branch=master)](https://coveralls.io/github/shadowmoose/RedditDownloader?branch=master)

[Click here to visit the documentation site!](https://shadowmoose.github.io/RedditDownloader/docs/site/User_Guide.html)

**Let's face it:** In this day and age, the internet is ephemeral. Anything anybody posts might be here one day,
and gone the next. Websites take down or move their images and videos, posts get hidden or removed, and their
content is lost. Even more so on Reddit, where accounts are constantly springing into existence -
and then vanishing as quickly without a trace. How's anybody supposed to keep their cherished cat picture 
collection around with all this change? Well fear not, my data-hoarding friend,
because Reddit Media Downloader is here for you!


**Reddit Media Downloader** is a program built to scan Comments & Submissions from multiple sources on Reddit, 
and download any media they contain or link to. It can handle scanning posts from your personal 
Upvoted/Saved lists, subreddits of your choice, user-curated multireddits, and more!
When it finds a Comment or Submission from wherever you specify, it will parse the text and links within to
find any media linked to. It then uses multiple downloaders to save this media locally onto your disk.


**RMD** comes equipped with a suite of options to let it scan just about anywhere you can find media on Reddit.
Coupled with its powerful baked-in Filter options to let you specify exactly what type of posts and comments
you're looking for (*"I only want Submissions with 'Unicorn' in the title, and no less than 1000 upvotes!"*), 
RMD makes automatically saving things a simple process. Built in Python and running headless (without a GUI), 
you can launch this program anywhere - and it's built from the ground-up to make automation a breeze.

[Check out the different places RMD can scan!](docs/site/Supported_Sources.md)

# RMD Can:
* Extract links inside comments, links in Submissions, and links within selfpost text.
* Work with links to most video sites, image hosts, and image blogs.
* Avoid saving duplicates of the same file, by using image recognition to compare similar pictures.
* Automatically seek to - and resume - where it last left off.
* Launch an in-console [Wizard](/docs/site/User_Guide.md#the-wizard) to make even the most complex configuration setups simple

# Requirements:
**Python**: You can download Python for your operating system from [https://www.python.org/downloads/](https://www.python.org/downloads/).

*The program will launch an assistant [Wizard](/docs/site/User_Guide.md#the-wizard) to help you set everything up, when run for the first time.*

**Please see [Here](https://shadowmoose.github.io/RedditDownloader/docs/site/User_Guide.html) for the guide to getting started.**


# Issues?
This program uses multiple Handlers, included in the *handlers* directory, to process the various links it finds. Many are extremely generic to allow for the widest possible site coverage.
If you hit any links which it does not support, find anything broken, or just need assistance, please open a new request [here](https://github.com/shadowmoose/RedditDownloader/issues/new).
