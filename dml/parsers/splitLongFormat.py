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
# import pandas as pd # constructing data



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

def trait_to_identifier(trait):
  trait_id = trait.split('_')[-1]

  # Check if the trait id is a location-year pair or otherwise
  # Set it's filename according to which identifier is used
  if is_location_year(trait_id):
    location, year = get_location_year(trait)
    trait_id = '_'.join([location, str(year)]).strip()
  else:
    trait_id = trait_id.strip()

  return trait_id

def trait_to_column(trait):
  result = '_'.join(trait.split('_')[:-1])
  if result == '': # in case of row label (left-most column label)
    return trait
  return result

def process(files):
  try:
    identifiers = {} # list of unique identifiers to name files
    column_names = [] # look up raw trait name given an index
    # For each file...
    # For each line...
    fp = fileinput.input(files)
    # STEP 1: Read through all of the files and data to allocate space
    for line in fp:
      # CASE: Header
      if (fp.filelineno() == 1):
        # Split the header into a list of values
        raw_trait_list = line.split(',')
        for index, trait in enumerate(raw_trait_list):
          column_names.append(trait.strip())
          local_column_names.append(trait.strip())
          # Add identifier as a unique filename
          tid = trait_to_identifier(trait)
          row_label = line.split(',')[0]
          if tid not in identifiers and tid != row_label:
            identifiers[tid] = {}
            identifiers[tid]['filename'] = '.'.join([tid, 'csv'])
            identifiers[tid]['header'] = [line.split(',')[0]] # Assume row label
            identifiers[tid]['data'] = None

        continue
        
      # CASE: Comment or blank line (skip)
      if line[0] == '#' or line[0] == '\n':
        continue

      # CASE: Normal row
      # We've reached a normal row that contains a line and all its values for
      # each trait
      try:
        identifiers[]
        line_values = line.split(",")
        for col, value in enumerate(line_values):
          if value == 'NA': # skip missing values
            continue
          else:
            label = line_values[0]
            value = value.strip()
            column_index = col
            column_name = trait_to_column(column_names[col])
            identity = trait_to_identifier(column_names[col])
            
            pprint((column_index, column_name, identity, label, value))
            # Ignore any identifiers that were not previously created
            if identity in identifiers:
              # If new trait is not in the file's header, append it
              if column_name not in identifiers[identity]['header']:
                identifiers[identity]['header'].append(column_name)
              # Save value by line/trait
              identifiers[label] = {}
              row_label = identifiers[identity]['header'][0]
              identifiers[label][row_label] = label
              
              # Header should exist now, so we add the line/trait value

  

            # Check if there is already a header for this column
            # If not, append it and its associated value
            # Step 1: Given column name, find it in header

      except:
        raise

    pprint(identifiers)
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
