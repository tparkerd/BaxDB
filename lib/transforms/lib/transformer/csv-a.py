"""
CSV Dataset Transformer A
v 1.0-alpha

Transform the long format of traits by line, where the trait contains location and
year. It splits a single file into N files, where N is the number of location
and year combinations.


Expected input:
  N files, M traits, P lines
  Line/Pedigree, LocationYear 4-tuple,  Trait 1, Trait 2, Trait 3, Trait 4...Trait M
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M

"""

import fileinput
import math
import os
import re
import sys
from pprint import pprint

import pandas as pd

from .. import helpers  # custom helper functions for transformation


def read_stdin(fp, delimiter):
  """
  Function that handles any textual data streamed in from stdin

  Args:
    fp (FileInupt): list of filenames
    delimiter (String): value to split data

  Returns:
    Pandas dataframe
  """
  data = []
  header = [ column.strip() for column in fp.readline().split(delimiter) ]
  typings = None
  for line in fp:
    line = [ cell.strip() for cell in line.split(delimiter) ]
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

def read_files(fp, delimiter):
  """
  Reads contents of a CSV file and creates a dataframe of it

  Args:
    fp (FileInput): list of filenames
    delimiter (String): value to split data

  Returns:
    Pandas dataframe
  """
  # Fill an empty dataframe with all the possible traits and lines
  df = pd.DataFrame()
  for line in fp:
    # Float precision helps to avoid rounding errors, but it does hurt performance
    df = pd.concat([df, pd.read_table(fp.filename(),
                    float_precision='round_trip', delimiter = delimiter)], axis = 0,
                    ignore_index = True, sort = False)
    fp.nextfile()
  return df

def process(args, delimiter = ','):
  """
  Process data

  Args:
    args (Namespace): arguments supplied by user
    delimiter (String): value to split data, default ','
  """
  files = args.files
  try:
    fp = fileinput.input(files)
    df = None
    if len(files) < 1:
      df = read_stdin(fp, delimiter)
    else:
      df = read_files(fp, delimiter)

    if df is None:
      raise Exception("No data supplied.")

    # Create a set of filenames and identifiers
    # The filenames are used to access the data stored as dataframes,
    # and the identifiers are used to filter the appropriate columns
    # to omit irrelevant data in the output dataframe
    filenames = set()
    identifiers = set()
    for trait in df.columns[1:]:
      filename = helpers.trait_to_filenames(trait)
      filenames.add(filename)
      identity = helpers.trait_to_identifier(trait)
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
      dfs[filename]['data'].columns = [ helpers.trait_to_column(t) for t in dfs[filename]['data'].columns ]

    # Return the resultant dataframes
    return dfs

  except:
    raise 

  # In case something went wrong, return None and test for that on response
  return None
