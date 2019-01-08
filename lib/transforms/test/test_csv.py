"""
Unit tester module for verifying the output of the `splitLongFormat` module
"""
import pytest
from pprint import pprint
from lib.transformer.csv import process
from lib.helpers import Convert
import math

def test_csv(args_csv, data_csv):
  args = args_csv
  src_data = data_csv
  resultant_files = process(args)

  src_processed_values = 0
  target_processed_value = 0

  # Compare each value from source to targets
  # For each row...
  for row in src_data.itertuples(index = True):
    for i, col in enumerate(src_data.columns.values):
      src_processed_values = src_processed_values + 1
      index_name = row[0]

      # Fetch names and values from source
      src_col_name = col
      src_value = row[i + 1]

      # For each value, translate the column as the filename, and use it to
      # to access the target file's data
      target_name = Convert.loyr_to_filename(Convert.trait_to_identifier(src_col_name))
      target_data = resultant_files[target_name]['data']

      # Fetch names and values from target file
      target_col_name = Convert.trait_to_column(src_col_name)
      
      # In case the source value is NAN, we need to make sure that there is not
      # an entry for the line in the target file. As such, the index for the
      # line should *not* be in the target file if there was no growout for said
      # line. However, if the line was part of the growout, but that value was
      # not measured, the value will be there, and it has to be checked for NAN
      print(f'{index_name}   <{target_name}>    ({src_col_name} -> {target_col_name})   sv: {src_value}', end = '')
      if math.isnan(src_value):
        # Check that index is not in target dataframe
        if index_name in target_data.index:
          # Make sure that is is also NAN, otherwise we have an error
          target_value = target_data.loc[[index_name], [target_col_name]].values[0,0]
          print(f'   tv: {target_value}')
          assert math.isnan(target_value)
        # Source NAN value was omitted from target file
        # Line was not present in growout (aka, location & year)
        else:
          print(f'   [{index_name} not in {target_name}]')
      else:
        target_value = target_data.loc[[index_name], [target_col_name]].values[0,0]
        print(f'   tv: {target_value}')
        assert math.isclose(src_value, target_value, rel_tol=1e-20)

  # Compare each value from targets to source
  # TODO

  # TODO: data point process between source and target, and asserting that
  #       the same number of *existing* data points were processed
  # mismatchcount = mismatchcount + 1
  # print(f'Value Mismatch:\n\t\t{src_col}\t{col}')
  # print(f'{row}\t{svalue}\t\t{tvalue}')
  # result = False