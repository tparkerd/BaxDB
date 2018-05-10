from configparser import ConfigParser
import psycopg2
import csv

def config(filename='database.ini', section='postgresql'):
  # create a parser
  parser = ConfigParser()
  # read config file
  parser.read(filename)

  # get section, default to postgresql
  db = {}
  if parser.has_section(section):
    params = parser.items(section)
    for param in params:
      db[param[0]] = param[1]
  else:
    raise Exception('Section {0} not found in the {1} file'.format(section, filename))

  return db

def connect():
  conn = None
  try:
    # read connection parameters
    params = config()

    # connect to the PostgreSQL server
    print('Connection to the PostgreSQL database...')
    conn = psycopg2.connect(**params)

    # create a cursor
    cur = conn.cursor()

    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    db_version = cur.fetchone()
    print(db_version)

    # Close the connection
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  
  return conn

def insert_species(conn, species):
  cur = conn.cursor()
  SQL = """INSERT INTO species (shortname, binomial, subspecies, variety)
        VALUES (%s, %s, %s, %s) RETURNING species_id;"""
  args_tuple = (species.n, species.b, species.s, species.v)
  cur.execute(SQL, args_tuple)
  newID = cur.fetchone()[0]
  conn.commit()
  cur.close()
  return newID

def find_species(conn, speciesShortname):
  cur = conn.cursor()
  cur.execute("SELECT species_id FROM species WHERE shortname = '%s';" %  speciesShortname)
  speciesID = cur.fetchone()[0]
  cur.close()
  return speciesID

def insert_population(conn, population): 
  cur = conn.cursor()
  SQL = """INSERT INTO population (population_name, population_species)
        VALUES (%s, %s) RETURNING population_id;"""
  args_tuple = (population.n, population.s)
  cur.execute(SQL, args_tuple)
  newID = cur.fetchone()[0]
  conn.commit()
  cur.close()
  return newID  

def find_population(conn, populationName):
  cur = conn.cursor()
  cur.execute("SELECT population_id FROM population WHERE population_name = '%s';" % populationName)
  populationID = cur.fetchone()[0]
  cur.close()
  return populationID

def generate_chromosome_list(numChromosomes):
  chrlist = []
  for count in range(1,numChromosomes+1):
    chrname = 'chr'+str(count)
    chrlist.append(chrname)
  return chrlist

def insert_chromosome(conn, chromosome):
  cur = conn.cursor()
  SQL = """INSERT INTO chromosome (chromosome_name, chromosome_species)
        VALUES (%s, %s) RETURNING chromosome_id;"""
  args_tuple = (chromosome.n, chromosome.s)
  cur.execute(SQL, args_tuple)
  newID = cur.fetchone()[0]
  conn.commit()
  cur.close()
  return newID

def insert_all_chromosomes_for_species(conn, numChromosomes, speciesID)
  chrlist = generate_chromosome_list(numChromosomes)
  insertedChromosomeIDs = []
  for chrname in chrlist:
    chrobj = chromosome(chrname, speciesID)
    insertedChromosomeID = insert_chromosome(conn, chrobj)
    insertedChromosomeIDs.append(insertedChromosomeID)
  return insertedChromosomeIDs

def find_chromosome(conn, chromosome_name, chromosome_species):
  cur = conn.cursor()
  # not sure if next line is correct...
  cur.execute("SELECT chromosome_id FROM chromosome WHERE chromosome_name = '%s' AND chromosome_species = '%s';" % chromosome_name, chromosome_species)
  chromosomeID = cur.fetchone()[0]
  cur.close()
  return chromosomeID

def parseLinesFromFile(lineFile):
  with open(lineFile) as f:
    linelist = f.readlines()
    for linename in linelist:
      linename = linename.rstrip()
  return linelist

def insert_line(conn, line):
  cur = conn.cursor()
  SQL = """INSERT INTO line (line_name, line_population)
        VALUES (%s, %s) RETURNING line_id;"""
  args_tuple = (line.n, line.p)
  cur.execute(SQL, args_tuple)
  newID = cur.fetchone()[0]
  conn.commit()
  cur.close()
  return newID

def insert_lines_from_file(conn, lineFile, populationID):
  linelist = parseLinesFromFile(lineFile)
  insertedLineIDs = []
  for linename in linelist:
    lineobj = line(linename, populationID)
    insertedLineID = insert_line(conn, lineobj)
    insertedLineIDs.append(insertedLineID)
  return insertedLineIDs

def find_line(conn, line_name):
  cur = conn.cursor()
  cur.execute("SELECT line_id FROM line WHERE line_name = '%s';" % line_name)
  lineID = cur.fetchone()[0]
  cur.close()
  return lineID

def insert_genotype(conn, genotype):
  cur = conn.cursor()
  SQL = """INSERT INTO genotype(line_ref, chromosome_id, genotype)
        VALUES (%s,%s,%s) RETURNING line_ref;"""
  args_tuple = (genotype.l, genotype.c, genotype.g)
  cur.execute(SQL, args_tuple)
  newID = cur.fetchone()[0]
  conn.commit()
  cur.close()
  return newID

class species:
  def __init__(self, shortname, binomial, subspecies, variety):
    self.n = shortname
    self.b = binomial
    self.s = subspecies
    self.v = variety

class population:
  def __init__(self, population_name, population_species):
    self.n = population_name
    self.s = population_species

class line:
  def __init__(self, line_name, line_population):
    self.n = line_name
    self.p = line_population

class chromosome:
  def __init__(self, chromosome_name, chromosome_species):
    self.n = chromosome_name
    self.s = chromosome_species

class genotype:
  def __init__(self, line_ref, genotype):
    self.l = line_ref
    self.c = chromosome_id
    self.g = genotype

if __name__ == '__main__':
  conn = connect()
  #########################################################
  # ADD A HARD-CODED SPECIES TO DB USING insert_species() #
  #########################################################
  #mySpecies = species('maize', 'Zea mays', None, None)
  #insertedSpeciesID = insert_species(conn, mySpecies)
  #print(insertedSpeciesID)

  ###############################################################
  # ADD A HARD-CODED POPULATION TO DB USING insert_population() #
  ###############################################################
  #myPopulation = population('Maize282',maizeSpeciesID)
  #insertedPopulationID = insert_population(conn, myPopulation)
  #print(insertedPopulationID)

  ###########################################################
  # LOOK UP ID OF A HARD-CODED SPECIES USING find_species() #
  ###########################################################
  maizeSpeciesID = find_species(conn, 'maize')
  print("SpeciesID of maize:")
  print(maizeSpeciesID)

  #################################################################
  # LOOK UP ID OF A HARD-CODED POPULATION USING find_population() #
  #################################################################
  maize282popID = find_population(conn, 'Maize282')
  print("PopulationID of Maize282:")
  print(maize282popID)

  #################################################################
  # LOOK UP ID OF A HARD-CODED CHROMOSOME USING find_chromosome() #
  #################################################################
  maizeChr1ID = find_chromosome(conn, 'chr1', maizeSpeciesID)
  print("ChromosomeID of Maize Chr1:")
  print(MaizeChr1ID) 

  ########################################################
  # GET LINES FROM SPECIFIED 012.indv FILE AND ADD TO DB #
  ########################################################
  #insertedLineIDs = insert_lines_from_file(conn, '/home/mwohl/Downloads/chr1_282_agpv4.012.indv', maize282popID)
  #print(insertedLineIDs)

  #################################################
  # ADD ALL CHROMOSOMES FOR A SPECIES TO DB USING #
  #################################################
  #insertedChromosomeIDs = insert_all_chromosomes_for_species(conn, 10, maizeSpeciesID)
  #print(insertedChromosomeIDs)

  #################################################################################################
  # GET GENOTYPES FROM SPECIFIED .012 FILE, CONVERT TO INT, AND ADD TO DB USING insert_genotype() #
  #################################################################################################
  rawGenos = []
  with open('/home/mwohl/Downloads/GWASdata/chr1_282_agpv4.012') as f:
    myreader = csv.reader(f, delimiter='\t')
    for item in myreader:
      item.pop(0)
      for i in range(len(item)):
        item[i] = int(item[i])
      rawGenos.append(item)
  
  lineIDlist = []
  for linename in linelist:
    linename = linename.rstrip()
    lineID = find_line(conn, linename)
    lineIDlist.append(lineID)

  zipped = zip(lineIDlist, rawGenos)
  ziplist = list(zipped)
  for zippedpair in ziplist:
    myGeno = genotype(zippedpair[0], maizeChr1ID, zippedpair[1])
    insertedGenoID = insert_genotype(conn, myGeno)
    print(insertedGenoID)