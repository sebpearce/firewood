#!/usr/bin/env python
# pyrewood.py
#
# Author: Seb Pearce
#
# Date: 2015-04-03
#
# Parses "My Clippings.txt" & creates a directory of text files based on
# book titles. Originally written in C, now in Python.
#

from sys import argv
import sys
import re
import os

# option to include metadata for each clipping
show_info = False

DEFAULT_FILENAME = "My Clippings.txt"

# Firewood will output into a directory with this name 
DIRNAME = "Kindle Clippings"

# each clipping always consists of 5 lines:
# - title line
# - clipping info/metadata
# - a blank line
# - clipping text
# - a divider made up of equals signs

# so we track the index of the lines we care about, and use MOD to extract the
# "type" of the line from the absolute line number of the file
TITLE_LINE = 0
CLIPPING_INFO = 1
CLIPPING_TEXT = 3
MOD = 5

if len(argv) >= 3:
  script, arg1, arg2 = argv
  if arg1 == "-i":
    show_info = True
    filename = arg2
  elif arg2 == "-i":
    show_info = True
    filename = arg1
  else:
    filename = arg1
elif len(argv) == 2:
  script, arg1 = argv
  if arg1 == "-i":
    show_info = True
    filename = DEFAULT_FILENAME
  else:
    filename = arg1
else:
  filename = DEFAULT_FILENAME

# check that file exists, otherwise exit
if not os.path.isfile(filename):
  print "ERROR: cannot find \"" + filename + "\"."
  print "Please make sure it is in the same folder as this script."
  print "If you've renamed it, enter the new file name like this:"
  print "\tpython pyrewood.py new_file_name.txt"
  sys.exit()

def remove_chars(s):
  # replace colons with a hyphen so "A: B" becomes "A - B"
  s = re.sub(' *: *', ' - ', s)  
  s = s.replace('?','')
  s = s.replace('&','and')
  # replace ( ) with a hyphen so "this (text)" becomes "this - text"
  s = re.sub('\((.+?)\)', r'- \1', s)  
  # delete filename chars tht are not alphanumeric or ; , _ -
  s = re.sub('[^a-zA-Z\d\s;,_-]+', '', s)  
  # trim off anything that isn't a word at the start & end
  s = re.sub('^\W+|\W+$', '', s)  
  return s

# create the output directory
if not os.path.exists(DIRNAME):
  os.makedirs(DIRNAME)

output_files = set() # set of titles already processed
title = metadata = ''

# open My Clippings.txt and read data in lines
infile = open(filename, 'r')
for line_num, x in enumerate(infile):
  # trim \r\n from line
  x = re.sub('[\r\n]','', x)
  # trim hex bytes at start if they're there
  if x[:3] == '\xef\xbb\xbf':
    x = x[3:]

  # if we're at a title line and it doesn't match the last title
  if line_num % MOD == TITLE_LINE:
    title = x
  elif line_num % MOD == CLIPPING_INFO:
    # include metadata (location, time etc.) if desired
    if show_info:
      metadata = x.replace('- Your Highlight on ','').replace('Added on ','')
    # otherwise, clear `metadata`
    else:
      metadata = ''
  elif line_num % MOD == CLIPPING_TEXT:
    # Skip trying to write if we have no body
    if x == '':
      continue

    # trim filename-unfriendly chars for outfile name
    outfile_name = remove_chars(title) + '.txt'

    # we want to `append` by default, but if this is the first time we're
    # seeing this title, we should set the mode to `write`
    mode = 'a'
    if outfile_name not in output_files:
      mode = 'w'
      output_files.add(outfile_name)

    path = DIRNAME + '/' + outfile_name
    with open(path, mode) as outfile:
      if metadata:
        # write out any necessary metadata
        outfile.write("%s\n\n" % metadata)
      # write out the current line (the clippings text)
      outfile.write("%s\n\n...\n\n" % x)

print "\nExported titles:\n"
for i in output_files:
  print "%s" % i

infile.close()

