from MTBTrailUrlParser import MTBTrailUrlParser
from MTBJsonLineParser import MTBJsonLineParser
from MTBTrailMongoDB import MTBTrailMongoDB
import multiprocessing
from multiprocessing import Pool
import time
import os

# ------------------------------------------------------------------
# This is the main mtb trails parser that uses the following files:
# 1. MTBJsonLineParser.py - parses the json lines file
# 2. MTBTrailUrlParser.py - parses each individual URL
# 2. MTBTrailParser.py - parses the actual trail html page
# ------------------------------------------------------------------
    
# Parse the trail url into tuple data
def parse_trail_url(trail_url):
    return trailUrlParser.parseTrail(trail_url)

# Collect the processed trail urls into tuples 
trailDataTuples = []
def collect_trail_data_tuples(tuple):
    if tuple is not None:
        trailDataTuples.append(tuple)
    #print(f"Trail data tuples len = {len(trailDataTuples)}")

# let's parse the json lines file to get all trail routes
jlFile = "../mtb-project-crawler/crawler/spiders/mtbproject.jl"
#jlFile = "test.jl" 
jsonLineParser = MTBJsonLineParser()
trail_urls = jsonLineParser.parse(jlFile)
print(f"Trail urls len = {len(trail_urls)}")

# ----------------------------------------------------
# POOL Layer for splitting the data across multiple
# nodes, currently this is still pretty slow even
# with chunking the main list into smaller pieces
# ----------------------------------------------------

# divide the trails into ranks
cpu_count = os.cpu_count()
trailsLen = len(trail_urls)
CHUNK_LEN = 1000
#CHUNK_LEN = 10

# loop through the json lines and parse each individual URL
trailUrlParser = MTBTrailUrlParser()

# Create new multiprocessing pool that takes trail urls and splits
print(f"CPU_COUNT = {cpu_count}")
pool = Pool(processes=cpu_count)
st = time.time()
#result_pool = pool.starmap_async(parse_trail_url, trail_urls[1:100],
result_pool = pool.map_async(parse_trail_url, trail_urls,
    chunksize=CHUNK_LEN, callback=collect_trail_data_tuples)
pool.close()
res = result_pool.get()
et = time.time()
elapsed = et - st
print("\nExecution time (Pooling): ", elapsed, " sec")
print(f"Result length = {len(res)}")
print("\n")

# --------------------------------------------------------
# Collect the data from multiprocessing into lists after
# parsing on multiples CPUs or Nodes
# --------------------------------------------------------

# let's get individual lists of the metadata and the descriptions separately
mtbTrailRoutes = list(zip(*trailDataTuples))[0] # list of objs
mtbTrailRouteDescriptions = list(zip(*trailDataTuples))[1] # list of lists of objs
print(f"Number of trail routes = {len(mtbTrailRoutes)}")
print(f"Number of trail route descriptions = {len(mtbTrailRouteDescriptions)}")
print(f"Trail data tuples len = {len(trailDataTuples)}")

# --------------------------------------------
# MongoDB Operations for deleting/inserting
# --------------------------------------------

# Initialize the TrailMongo DB using ATLAS 
#trailMongoDB = MTBTrailMongoDB()
#db = trailMongoDB.get_database()

# This is needed when we need new INDEXES for the collections
trailMongoDB.create_indexes()

# let's first serialize the mtb trail route data so that it can be inserted
newMTBTrailRoutes = trailMongoDB.serialize_mtb_trail_route_data(mtbTrailRoutes)
print(f"New Mtb Trail Routes len = {len(newMTBTrailRoutes)}")
print(newMTBTrailRoutes)
print("\n")

print(f"New Mtb Trail descriptions len = {len(mtbTrailRouteDescriptions)}")
print("First element in the descriptions:")
print(f"First descs len = {len(mtbTrailRouteDescriptions[0])}")
print(mtbTrailRouteDescriptions[0])
print("\n")

# let's delete all records from the DB tables
trailMongoDB.delete_mtb_trail_route_data()

# insert the mtb trail routes to the mongoDB
trailMongoDB.insert_mtb_trail_routes(newMTBTrailRoutes)

# insert the mtb trail route descriptions to the mongoDB
trailMongoDB.insert_mtb_trail_route_descriptions(mtbTrailRouteDescriptions)

"""
# play around with data
find_mtb_trail_data(db)
"""
