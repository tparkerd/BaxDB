#!/usr/bin/env python3
"""
Parse the long format of traits by line, where the trait contains location and
year. It splits a single file into N files, where N is the number of location
and year combinations.

Common usage:
  python splitLongFormat.py -v input_file

Expected ouput:
  N files, M traits, P lines
  Line/Pedigree, Trait 1, Trait 2, Trait 3, Trait 4...Trait M
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M
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

def process_stdin(fp):
  """
  Function that handles any textual data streamed in from stdin

  Args:
    fp (FileInupt): 

  Returns:
    Pandas dataframe
  """
  data = []
  header = [ column.strip() for column in fp.readline().split(',') ]
  typings = None
  for line in fp:
    line = [ cell.strip() for cell in line.split(',') ]
    # Covert strings of numeric values to numeric type
    for index, value in enumerate(line):
      # Check if it's an integer, float, or some variation of NA(N)
      if re.compile(r'(^\-?\d+(.?\d+)?$)|(^[nN][aA][nN]?)$').search(value):
        if 'na' in value.lower():
          line[index] =  math.nan
        else:
          try:
            line[index] = float(value)
          except ValueError:
            print (f'`{str(value)}` cannot be cast as float.')
    # Verify that the current row has the same typings as previous row
    # CASE: Typings have not been established
    if typings is None:
      typings = [ type(cell) for cell in line ]
    else:
      try:
        for index, value in enumerate(line):
          if not isinstance(value, typings[index]):
            raise TypeError(f"`{value}` does not match column type of {typings[index]}. Check for extra headers or comments.")

      except:
        raise
    data.append(line)

  df = pd.DataFrame.from_records(data, columns = header)
  return df

def process_files(fp):
  """
  Reads contents of a CSV file and creates a dataframe of it

  Args:
    fp (FileInput): list of filenames

  Returns:
    Pandas dataframe
  """
  # Fill an empty dataframe with all the possible traits and lines
  df = pd.DataFrame()
  for line in fp:
    # Float precision helps to avoid rounding errors, but it does hurt performance
    df = pd.concat([df, pd.read_csv(fp.filename(),
                    float_precision='round_trip')], axis = 0,
                    ignore_index = True, sort = False)
    fp.nextfile()
  return df

def process():
  files = args.files
  try:
    fp = fileinput.input(files)
    df = None
    if len(files) < 1:
      df = process_stdin(fp)
    else:
      df = process_files(fp)

    # Create a set of filenames and identifiers
    # The filenames are used to access the data stored as dataframes,
    # and the identifiers are used to filter the appropriate columns
    # to omit irrelevant data in the output dataframe
    filenames = set()
    identifiers = set()
    for trait in df.columns[1:]:
      filename = trait_to_filenames(trait)
      filenames.add(filename)
      identity = trait_to_identifier(trait)
      identifiers.add(identity)
    filenames = sorted(list(filenames))
    identifiers = sorted(list(identifiers))

    dfs = {}
    for index, filename in enumerate(filenames):
      dfs[filename] = {}
      dfs[filename]['filename'] = '.'.join([filename, 'csv'])
      identity = identifiers[index]
      # Create a regex pattern that joins the identifier with Boolean ORs
      # Also, make it so that it can be anywhere in the column name and be
      # included.
      pattern = f".*{'|'.join([list(df)[0], identity])}.*"
      # Only include relevant column, set row label as index, and drop any rows that have all missing values
      dfs[filename]['data'] = df.filter(regex = pattern).set_index(list(df)[0]).dropna(how = 'all')
      # Rename columns to omit location-year pairs
      dfs[filename]['data'].columns = [ trait_to_column(t) for t in dfs[filename]['data'].columns ]
      
    # Output the files
    try:
      if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    except Exception as e:
      raise
    for df in dfs.keys():
      if (args.verbose):
        pprint(dfs[df])
      dfs[df]['data'].to_csv(os.path.join(str(args.outdir), dfs[df]['filename']))
    pprint(f"Created {len(dfs.keys())} files in {args.outdir}")

  except:
    raise 

if __name__=="__main__":
  global args
  parser = argparse.ArgumentParser()
  parser.add_argument('files', metavar='FILE', nargs='*',
                      help='files to read, if empty, stdin is used')
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="increase output verbosity")
  parser.add_argument("-o", "--outdir", default = f"output_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}",
                      help="name of output directory")
  args = parser.parse_args()

  process()
