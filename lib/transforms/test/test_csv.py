#!/usr/bin/env python3
"""
Unit tester module for verifying the output of the `splitLongFormat` module
"""
import fileinput
import argparse
import datetime
from pprint import pprint
import pandas as pd
import sys
import os
import math
import re

def contentsMatch(src, target):
  """
  For every data point in the target, compare it to the value stored in the source
  """
  global args
  global filecount
  global valuecount
  global mismatchcount

  # This may involve dealing with rounding issues
  tdf = pd.read_csv(target, index_col = 0, float_precision='round_trip')
  suffix = f'{target[:2]}{target[-6:-4]}'
  if suffix == 'ravg': # hard-coded out of laziness
    suffix = 'rankAvg'

  result = True

  # For each row...
  for row in list(tdf.index.values):
    # For each column...
    for col in list(tdf.columns.values):
      valuecount = valuecount + 1
      src_col = f'{col}_{suffix}'
      tvalue = tdf.at[row, col]
      svalue = src.at[row, src_col]
      # If not NANs
      if math.isnan(svalue) and math.isnan(tvalue):
        # result = True
        pass
      # Floating point value is reasonably close
      elif math.isclose(svalue, tvalue, rel_tol=1e-20) == True:
        # result = True
        pass
      else:
        mismatchcount = mismatchcount + 1
        print(f'Value Mismatch:\n\t\t{src_col}\t{col}')
        print(f'{row}\t{svalue}\t\t{tvalue}')
        result = False

  return result

def runtests():
  global args
  global filecount
  global valuecount
  global mismatchcount
  src = args.files[0]
  files = sorted(os.listdir(args.directory))
  # Source dataframe
  sdf = pd.read_csv(src, index_col=0, float_precision='round_trip')

  os.chdir(args.directory)
  result = True
  for file in files:
    filecount = filecount + 1
    if contentsMatch(sdf, file) == False:
      result = False
  return result

if __name__=="__main__":
  global args
  global filecount
  global valuecount
  global mismatchcount
  parser = argparse.ArgumentParser()
  parser.add_argument('files', metavar='FILE', nargs='*', default = ['in'],
                      help='files to read, if empty, stdin is used')
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="increase output verbosity")
  parser.add_argument("-d", "--directory", required = True, help="name of output directory")
  args = parser.parse_args()

  filecount = 0
  valuecount = 0
  mismatchcount = 0
  if runtests() == True:
    print(f'{valuecount} value(s) were checked in {filecount} file(s).\nNo issues found. All values are correct.')
  else:
    print(f'{valuecount} value(s) were checked in {filecount} file(s).\n{mismatchcount} problem(s) were found.')