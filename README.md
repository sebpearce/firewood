Firewood
========

Firewood parses Kindle's "My Clippings.txt" and outputs text files, organized by title.

Useful if you want to be able to skim through the best bits of books you've already read and highlighted. Could also be used with `grep` or some similar search tool to find a particular term in a book.

Firewood will create a directory called `Kindle Clippings` and will save all text files there.

Usage
-----
####The easy way####
Put the `firewood.app` in the same directory as `My Clippings.txt`, then double-click `firewood.app`. This is an AppleScript that will open a terminal window and run the application.

If you get an error message about an “unidentified developer”, try this:

1. right-click the .app file
2. hold the alt/option key
3. click `open`

####The regular way####
Run `make` to create the executable. Put the executable in the same directory as `My Clippings.txt` (this can be found in the Kindle's `documents` directory.)

Run it by executing `./firewood`.

**UPDATE (2015-04-06):** I've rewritten Firewood in Python to make it easier for me to tinker with. The new version is `pyrewood.py`. You can run it as a script by putting it in the same directory as your `My Clippings.txt` and doing `python pyrewood.py` from the terminal.

