title: Running & Configuring

# Running and Configuring RMD
*Reddit Media Downloader is simple to use, but also has many powerful configuration options 
to help you get exactly what you want downloaded. 
We'll briefly cover the basics you'll need to get started here.*

## Starting RMD
Once [you've installed RMD](Installing.md), you can run RMD at any time by launching ```Run.py```.

If you'd prefer to use a terminal, RMD can be started using using the terminal command:

```python Run.py```

*Note: If there are multiple Python installations on your machine, make sure you're running with python3.*

When run for the first time, RMD will download any additional libraries it requires. 
Once finished, you may be required to re-launch RMD.

## First-time setup
Once you've launched RMD for the first time, the terminal will prompt you to enter some first-time setup configs. 
I suggest using the defaults, which will open a "WebUI" user interface to make configuring easier.

Once the WebUI has started, you'll want to authorize RMD to read from Reddit on your behalf.

*If you do not wish to (or cannot) use the WebUI, run RMD with the ```--authorize``` flag, to enable in-console authentication.*

## Authorizing RMD
Allowing RMD read-only access to Reddit is very simple from the Web Interface.
Simply navigate to the __"Settings"__ tab, and click the link under the "Auth" section.

This will redirect your browser to Reddit, which will prompt you to grant RMD access.

Once you've authorized an account, [check out the __"Sources"__ tab](Sources.md) to start finding new Posts.

**Note:** This process does *not* allow RMD to read your password, edit your data, or do anything other than read reddit.
Specifically, RMD will gain access to *read*:

+ Liked & Saved Posts
+ Private Subreddits and feeds you have access to
+ Public Posts made to the rest of Reddit by all users

