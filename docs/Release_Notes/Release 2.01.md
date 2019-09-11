# Release 2.01
This is a small release to patch known bugs from Release 2.0.

This fixes a crash, and some file naming issues.
Specifically, this fixes #23, and (finally) closes #19.

Special thanks to @parkerlreed and @GreysenEvans for going to great lengths to help track down tricky bugs!

**Note:** This patch requires a new library to sanitize filenames, so make sure you update the requirements if you pull directly from Git!

### Changelog

+ Expanded support for characters in filenames.
+ Fixed bug causing crash related to certain terminals.
