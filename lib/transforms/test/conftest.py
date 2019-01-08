"""
Main test module for testing data transformations
"""

import pytest
import unittest
import pandas as pd
from unittest.mock import patch
from main import parseOptions as po

@pytest.fixture(scope='module')
def data_csv():
  try:
    # Float precision helps to avoid rounding errors, but it does hurt
    # performance
    df = pd.read_csv('./test/data/csv', float_precision='round_trip',
                      index_col='Pedigree')
  except:
    raise

  return df

@pytest.fixture(scope='module')
def args_csv():
  with patch('sys.argv', ['-v', '--debug', '-t', 'csv', './data/in']):
    return po()
