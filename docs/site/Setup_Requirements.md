# Setup:
1. **[Get Python Installed.](https://www.python.org/downloads/)** - Typically the latest version will do. 
(See [Supported Versions](#supported-python-versions))
2. **Download:** Download this program, either using git or by [clicking here](https://github.com/shadowmoose/RedditDownloader/releases/latest) *(Latest Release)*. If you download the zip, unpack it.
3. **Install dependencies:** launch a terminal inside wherever you saved the program folder, and run the line:
```pip install -r requirements.txt```

4. Once the install finishes, launch the program with:

```python main.py```

*On first launch, it will run an assistant to aid in the setup process.*

## Notes:

* Whenever desired, you can automatically update the program and its dependencies by running:

```python main.py --update```

* ...or by manually downloading the latest release and re-running:

```pip install -r requirements.txt```

See [Here](../Arguments.md) for more information on (optional) parameters, for advanced use & automation.

See [User-Guide](./User_Guide.md) for examples on running now that it's been set up.

## Supported Python Versions:
You should be fine with 3.4 up, and maybe even slightly earlier, but you can view the only versions I officially support at [The Travis Build Page](https://travis-ci.org/shadowmoose/RedditDownloader). It automatically checks the most recent commit, and runs through a strict set of tests to make sure nothing's broken.
