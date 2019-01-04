"""
Data Transformer Script

Takes in 

Common usage:
  python splitLongFormat.py -v input_file

Expected ouput:
  N files, M traits, P lines
  Line/Pedigree, Trait 1, Trait 2, Trait 3, Trait 4...Trait M
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M

Background:
  Turns out the file that this was created for changed 

  TODO(timp): Take everything that isn't file specific out and put it into its
              module. Make separate files/modules with just functions that can 
              parse files and will be the 'versions' of parsers
"""

import argparse
import datetime
import importlib
import os
from pprint import pprint


def process(args):
  try:
    # Determine the type of parser to use
    directory = './lib/parsers'
    parsers = set([ f[:-3] for f in os.listdir(directory) if not f.startswith('_') and f.endswith('.py') ])
    modulepath = directory.replace('.', '').replace('/', '', 1).replace('/', '.')

    # Import the user-specified parser if it exists
    if args.parser not in parsers:
      if args.parser is None:
        raise Exception("No parser was supplied. Cannot process data. Aborting.")
      else:
        raise Exception("Unknown parser. Aborting.")
    else:
      parser = importlib.import_module(f'{modulepath}.{args.parser}')

    # Pass args to the chosen parser and get back resultant data
    dfs = parser.process(args)

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
  parser = argparse.ArgumentParser()
  parser.add_argument('files', metavar='FILE', nargs='*',
                      help='files to read, if empty, stdin is used')
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="increase output verbosity")
  parser.add_argument("-o", "--outdir", default = f"output_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}",
                      help="name of output directory")
  parser.add_argument("-p", "--parser", default = None, help = "name of parser")
  args = parser.parse_args()

  process(args)
