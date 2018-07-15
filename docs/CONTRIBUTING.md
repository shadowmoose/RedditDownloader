# Contribution Guidelines:

All contributions too RMD are welcome! I appreciate any help I can get.

That said; There are a few things to keep in mind in order to make the process run smoothly for everybody:

### 1. If you're fixing a bug or adding something new, let us know.
* If repairing a bug, please leave a message on the bug's report informing everyone it's being worked on.
* Make sure you check first to see if anybody else has already submitted a fix.
* If you're adding something new or changing existing systems, either open an Issue or message shadowmoose about it.
* This is simply to avoid doubling effort and wasting time.

### 2. I'm going to have to review everything submitted.
* Obviously, I'm going to have to review all the code submitted to the project.
* Depending on my schedule, this could take some time, so please be patient!
  
### 3. TravisCI is probably not going to run your PR properly.
* The test build uses some private testing data that will not be exposed to outside builds.
* In most/all cases, this will mean your build will fail the initial test once it's submitted.
* This is fine. Your changes will be manually evaluated after review. Just make sure you've tested it locally.

### 4. Document your reasoning behind the changes.
* This one is pretty obvious, but please make the description of your changes as detailed as is appropriate.

### 5. If you bring in a new library or change an existing one, document it.
* For any new or changed links to external libraries, I expect an explanation for why it is needed.
* Additionally, you *must* provide a link to the lib's home page.
* However the lib is imported/embeded, you should also include where to find the link used on the lib's documentation.
* Any PRs requiring undocumented packages or embedding CDN links without explanation will be denied.

### 6. Any obfuscated code, or code deliberately difficult to read, will be denied.
* This should go without saying, but if I can't read your code, it's not making it in.
* Where possible, try to maintain best practices with code style. In most cases, this includes PEP8 for Python.

**That's about it! Just use common sense and everything will be easy.**

*If you have any questions/concerns, feel free to open an Issue or message ShadowMoose.*
