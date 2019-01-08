"""
Helper Functions for data transformation script
"""

import datetime
import pandas as pd
import fileinput
import re
import math

class Convert:
  """
  Common conversion methods for data transformations
  """

  @classmethod
  def expand_location_code(cls, code):
    """
    Convert a location code (String) to its full name. The file `locations.csv`
    contains a dictionary of the key-value pairs. If original string is
    returned, check the `locations.csv` for its definition.

    Args:
      code (String): abbreviation for location

    Returns (String):
      Return full string of value if defined in locations dictionary, otherwise
      returns the original string value.

    Example cases:
      >>> expand_location_code('FL')
      'Florida'
      >>> expand_location_code('PU')
      'Purdue'

    """
    location_fp = 'locations.csv'
    locations = pd.read_csv(location_fp, index_col = 0)
    if code.upper() in locations.index:
      return locations.loc[code.upper()]['Name']
    else:
      return code

  @classmethod
  def is_location_year(cls, trait):
    """
    Determine if value is a (location code, year) pair

    Args:
      trait (String):

    Returns (Boolean):
      Return True if value is a valid (location, year) pair, False otherwise.

    Example cases:
      >>> is_location_year(FL06)
      True
      >>> is_location_year(FLA10)
      False
      >>> is_location_year(WR10)
      True
      >>> is_location_year(0242)
      False
      >>> is_location_year(FLAG)
      False

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

  @classmethod
  def get_location_year(cls, trait):
    """
    Determine if value is a (location code, year) pair

    Args:
      trait (String):

    Returns (String, Int):
      Return True if value is a valid (location, year) pair, False otherwise.

    Example cases:
      FL06 - FL, 2006
      FLA10 - FL, 2010
      WR10 - WR, 2010
      PU98 - PU, 1998

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

    return location_code, year

  @classmethod
  def loyr_to_filename(cls, trait):
    """
    Extract the location and year from a trait

    Args:
      trait (String):

    Returns (String):
      Return a new string as the basename (without extension) of a filename

    Example cases:
      FL06 - FL_2006
      FLA10 - FL_2010
      WR10 - WR_2010
      PU98 - PU_1998
    """
    trait_id = trait.split('_')[-1]

    # Check if the trait id is a location-year pair or otherwise
    # Set it's filename according to which identifier is used
    if cls.is_location_year(trait_id):
      location, year = cls.get_location_year(trait)
      trait_id = '_'.join([location, str(year)]).strip()
    else:
      trait_id = trait_id.strip()

    return trait_id

  @classmethod
  def trait_to_identifier(cls, trait):
    """Strip string of whitespace so that it can be used as an identifier to search the dataset with.

    Args:
      trait (String):

    Returns (String):
      Return a new string as the basename (without extension) of a filename

    Example cases:
      >>> trait_to_identifier('FL06')
      'FL06'
      >>> trait_to_identifier('WR10\n')
      'WR10'
      >>> trait_to_identifier('PU98\r\n')
      'PU98'
    """
    trait_id = trait.split('_')[-1]

    # Check if the trait id is a location-year pair or otherwise
    # Set it's filename according to which identifier is used
    if cls.is_location_year(trait_id):
      trait_id = trait_id.strip()
    else:
      trait_id = trait_id.strip()

    return trait_id

  @classmethod
  def trait_to_column(cls, trait):
    """Remove trailing location-year value from trait string.

    TODO(timp): Rename this and refactor `process` methods in transformers
    so that accurately reflect that it just clips off the trailing
    location-year pair for CSV format.

    Args:
      trait (String):

    Returns (String):
      Return a new string as the basename (without extension) of a filename

    Example cases:
      >>> trait_to_column('weight_FL06')
      'weight'
      >>> trait_to_column('B11_lmResid_MO06')
      'B11_lmResid'
    """
    result = '_'.join(trait.split('_')[:-1])
    if result == '': # in case of row label (left-most column label)
      return trait
    return result

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

def read_data(args, delimiter):
  """Reads in the data from either STDIN or a list of files

  Args:
    args (Namespace): arguments supplied by user
  
  Result:
    Pandas DataFrame
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
  except:
    raise

  return df