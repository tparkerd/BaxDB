"""
Helper Functions for data transformation script
"""

import datetime
# from pprint import pprint
# import pandas as pd
# import sys
# import os
# import math
# import re

def is_location_year(trait):
  """
  """
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
  """
  """
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
  """
  """
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
  """
  """
  trait_id = trait.split('_')[-1]

  # Check if the trait id is a location-year pair or otherwise
  # Set it's filename according to which identifier is used
  if is_location_year(trait_id):
    trait_id = trait_id.strip()
  else:
    trait_id = trait_id.strip()

  return trait_id

def trait_to_column(trait):
  """
  """
  result = '_'.join(trait.split('_')[:-1])
  if result == '': # in case of row label (left-most column label)
    return trait
  return result