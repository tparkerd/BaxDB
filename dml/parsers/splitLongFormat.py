#!/usr/bin/env python3
# Parse the long format of traits by line, where the trait contains location and
# year. It splits a single file into N files, where N is the number of location
# and year combinations.
# Expected ouput:
# N files, M traits, P lines
# Line/Pedigree, Trait 1, Trait 2, Trait 3, Trait 4...Trait M
# Line 1, 1, 2, 3, 4, 5...M
# Line 2, 1, 2, 3, 4, 5...M
# ...
# Line P, 1, 2, 3, 4, 5...M

import fileinput
import argparse
import shutil # added for shutil.rmtree for deleting directory

class AutoRepr(object):
  def __repr__(self):
    items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
    return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))

class datapoint(AutoRepr):
  def __init__(self, location, year, trait, line, value = None):
    self.location = location
    self.year = year
    self.trait = trait
    self.line = line
    self.value = value
  pass

def process(files):
  try:
    # For each file...
    # For each line...
    fp = fileinput.input(files)
    for line in fp:
      # If it's the header of the file, create a data matrix
      print(fp.filelineno())
      # if (fp.filelineno() == 1):
      # Skip comments and blank lines
      if line[0] == '#' or line[0] == '\n':
        continue
      try:
        pass
        print(line)
        # (key, val) = line.rstrip().split(',')
      except:
        pass

  except:
    raise 

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('files', metavar='FILE', nargs='*',
                      help='files to read, if empty, stdin is used')
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="increase output verbosity")
  args = parser.parse_args()

  process(args.files)
