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

default_filename = "My Clippings.txt"

# Firewood will output into a directory with this name 
dirname = "Kindle Clippings"

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
    filename = default_filename
  else:
    filename = arg1
else:
  filename = default_filename

# check that file exists, otherwise exit
if not os.path.isfile(filename):
  print "ERROR: cannot find \"" + filename + "\"."
  print "Please make sure it is in the same folder as this script."
  print "If you've renamed it, enter the new file name like this:"
  print "\tpython pyrewood.py new_file_name.txt"
  sys.exit()

# each clipping always consists of 5 lines
title_line = 1
clipping_info = 2
blank_line = 3
clipping_text = 4
equals_line = 5


def remove_chars(str):
  # replace colons with a hyphen so "A: B" becomes "A - B"
  str = re.sub(' *: *', ' - ', str)  
  str = str.replace('?','')
  str = str.replace('&','and')
  # replace ( ) with a hyphen so "this (text)" becomes "this - text"
  str = re.sub('\((.+?)\)', r'- \1', str)  
  # delete filename chars tht are not alphanumeric or ; , _ -
  str = re.sub('[^a-zA-Z\d\s;,_-]+', '', str)  
  # trim off anything that isn't a word at the start & end
  str = re.sub('^\W+|\W+$', '', str)  
  return str

# create the output directory
if not os.path.exists(dirname):
  os.makedirs(dirname)

current_line = 1 # line counter
list_of_titles = [] # list of titles already processed
list_of_output_files = [] # list of titles already processed
last_title = ''

# open My Clippings.txt and read data in lines
infile = open(filename, 'r')
data = infile.readlines()

# for each line
for x in data:

  # trim \r\n from line
  x = re.sub('[\r\n]','', x)
  # trim hex bytes at start if they're there
  if x[:3] == '\xef\xbb\xbf':
    x = x[3:]

  # if we're at a title line and it doesn't match the last title
  if current_line == title_line:
    if x != last_title:
      # check if we've already seen that title
      if x not in list_of_titles:
        # if not, we have a new book - add it to the list
        list_of_titles.append(x)
        last_title = x
        # trim filename-unfriendly chars for outfile name
        outfile_name = remove_chars(x) + '.txt'
        # open outfile for writing
        path = dirname + '/' + outfile_name
        outfile = open(path, 'w')
        # add the new filename to the list to display at the end
        list_of_output_files.append(outfile_name)
      else:
        # close last title's outfile
        outfile.close()
        # found title match, so reopen old file and append
        outfile_name = remove_chars(x) + '.txt'
        path = dirname + '/' + outfile_name
        outfile = open(path, 'a')

  # include metadata (location, time etc.) if desired
  elif current_line == clipping_info and show_info == True:
    x = x.replace('- Your Highlight on ','')
    x = x.replace('Added on ','')
    outfile.write("%s\n\n" % x)

  # the body of the clipping
  elif current_line == clipping_text:
    outfile.write("%s\n\n...\n\n" % x)

  current_line = current_line + 1
  if current_line >= 6:
    current_line = 1

print "\nExported titles:\n"
for i in list_of_output_files:
  print "%s" % i

outfile.close()
infile.close()

