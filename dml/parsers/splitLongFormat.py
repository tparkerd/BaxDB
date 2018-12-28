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
import datetime
from pprint import pprint # for debugging purposes
import pandas as pd # constructing data
import sys
import os


class AutoRepr(object):
  def __repr__(self):
    items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
    return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))

class datapoint(AutoRepr):
  def __init__(self, index, filename, location, year, trait, line, value):
    self.index = index
    self.filename = filename
    self.location = location
    self.year = year
    self.trait = trait
    self.line = line
    self.value = value
  pass

def is_location_year(trait):
  # If it's not four characters, it's not a location-year pair
  if len(trait) != 4:
    return False

  # If the last two characters are not integers, it's not a location-year pair
  if trait[-2:].isdigit() == False:
    return False

  # If the first two characters are not letters, it's not a location-year pair
  if trait[0:1].isalpha() == False:
    return False

  return True

def get_location_year(trait):
  # Get the location and year from the last four characters
  location_code = trait[-4:-2]
  # When the last two digits of a year are larger than the current year,
  # then assume that the experiment was done in the 1900s
  year = None
  dd = datetime.datetime.strptime(trait[-2:],'%y').year
  if dd > datetime.datetime.now().year:
    year = dd.replace(year = dd - 100)
  else:
    year = dd

  if year is None:
    raise Exception("Unable to convert `" + str(trait) +
                    "` to location-year pair. <location_code: " + location_code
                    + ", year: " + str(year) + ">")

  return (location_code, year)

def trait_to_filenames(trait):
  trait_id = trait.split('_')[-1]

  # Check if the trait id is a location-year pair or otherwise
  # Set it's filename according to which identifier is used
  if is_location_year(trait_id):
    location, year = get_location_year(trait)
    trait_id = '_'.join([location, str(year)]).strip()
  else:
    trait_id = trait_id.strip()

  return trait_id

def trait_to_identifier(trait):
  trait_id = trait.split('_')[-1]

  # Check if the trait id is a location-year pair or otherwise
  # Set it's filename according to which identifier is used
  if is_location_year(trait_id):
    trait_id = trait_id.strip()
  else:
    trait_id = trait_id.strip()

  return trait_id

def trait_to_column(trait):
  result = '_'.join(trait.split('_')[:-1])
  if result == '': # in case of row label (left-most column label)
    return trait
  return result

def process_stdin():
 return pd.read_csv(sys.stdin)

def process_files(fp):

  # Fill an empty dataframe with all the possible traits and lines
  df = pd.DataFrame()
  for line in fp:
    df = pd.concat([df, pd.read_csv(fp.filename())], axis = 0,
                    ignore_index = True, sort = False)
    fp.nextfile()
  return df



def process(files):
  try:
    fp = fileinput.input(files)
    df = None
    if len(files) < 1:
      df = process_stdin()
    else:
      df = process_files(fp)
    pprint(df)

    pprint(list(df))
    filenames = set()
    for trait in list(df)[1:]: # Omit row label
      filename = trait_to_filenames(trait)
      filenames.add(filename)
    pprint(filenames)


    identifiers = set()
    for trait in list(df)[1:]: # omit row label
      identity = trait_to_identifier(trait)
      identifiers.add(identity)

    identifiers = list(identifiers)

    pprint(identifiers)

    dfs = {}
    for index, filename in enumerate(filenames):
      dfs[filename] = {}
      dfs[filename]['filename'] = '.'.join([filename, 'csv'])
      
      print(identifiers[index])
      cases = [list(df)[0], identifiers[index]]
      pattern = '|'.join(cases)
      pattern = '.*' + pattern + '.*'
      # Only include relevant column, set row label as index, and drop any rows that have all missing values
      dfs[filename]['data'] = df.filter(regex = pattern).set_index(list(df)[0]).dropna(how = 'all')
      # Rename columns to omit location-year pairs
      dfs[filename]['data'].columns = [ trait_to_column(t) for t in dfs[filename]['data'].columns ]
      
    # Output the files
    output_dir = 'output_' + str(datetime.datetime.now())
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    for df in dfs.keys():
      pprint(dfs[df]['data'])
      dfs[df]['data'].to_csv(os.path.join(output_dir, dfs[df]['filename']))


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