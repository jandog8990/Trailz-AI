from MTBTrailUrlParser import MTBTrailUrlParser
from MTBJsonLineParser import MTBJsonLineParser
from MTBTrailMongoDB import MTBTrailMongoDB
import multiprocessing
from multiprocessing import Pool
import numpy as np
import time
import os

# ------------------------------------------------------------------
# This is the main mtb trails parser that uses the following files:
# 1. MTBJsonLineParser.py - parses the json lines file
# 2. MTBTrailUrlParser.py - parses each individual URL
# 3. MTBTrailParser.py - parses the actual trail html page
# ------------------------------------------------------------------

# let's parse the json lines file to get all trail routes
jlFile = "../mtb-project-crawler/mtbproject.jl"
st = time.time()
jsonLineParser = MTBJsonLineParser()
trail_urls = jsonLineParser.parse(jlFile)
et = time.time()
elapsed = et - st
#trail_urls = trail_urls[1:10]
print(f"Json Line Parser time = {elapsed} sec")
print(f"Trail urls len = {len(trail_urls)}")
print("\n")

"""
index_urls = [url for url in trail_urls if "index.php" in url]
print(f"Len index url = {len(index_urls)}")
print("Index url 0:")
print(index_urls[0])
print("\n")
"""

# ----------------------------------------------------
# Parse trail url function for parsing trail data
# ----------------------------------------------------
trailUrlParser = MTBTrailUrlParser()
def parse_trail_url(trail_url):
    return trailUrlParser.parseTrail(trail_url) 

# ----------------------------------------------------
# POOL Layer for splitting the data across multiple
# nodes, currently this is still pretty slow even
# with chunking the main list into smaller pieces
# ----------------------------------------------------

# multiprocessing pool that takes trail urls and batches
cpu_count = os.cpu_count()
CHUNK_LEN = 25 
pool = Pool(processes=cpu_count)
st = time.time()
result = pool.map_async(parse_trail_url, trail_urls,
        chunksize=CHUNK_LEN)
pool.close()
res = result.get()
et = time.time()
elapsed = et - st
print("\n")
print(f"CPU count = {cpu_count}")
print(f"Execution time (pooling): {elapsed} sec")
print(f"Result len = {len(res)}")
print("\n")

# trail data tuples
trailDataTuples = [t for t in res if t]

# --------------------------------------------------------
# Collect the data from multiprocessing into lists after
# parsing on multiples CPUs or Nodes
# --------------------------------------------------------

# let's get individual lists of the metadata and the descriptions separately
mtbTrailRoutes = list(zip(*trailDataTuples))[0] # list of objs
mtbTrailRouteDescriptions = list(zip(*trailDataTuples))[1] # list of lists of objs

# MTB trail route descriptions
missingIndices = [i for i in range(len(mtbTrailRouteDescriptions))
    if len(mtbTrailRouteDescriptions[i]) == 0]
print(f"Missing Descriptions len = {len(missingIndices)}") 
print(missingIndices)
print("\n")
missingTrailRoutes = np.take(mtbTrailRoutes, missingIndices)

# remove the missing elements
mtbTrailRouteDescriptions = [mtbTrailRouteDescriptions[i] for i in 
    range(len(mtbTrailRouteDescriptions)) if i not in missingIndices]
mtbTrailRoutes = [mtbTrailRoutes[i] for i in
    range(len(mtbTrailRoutes)) if i not in missingIndices]
print(f"MTB trail routes len = {len(mtbTrailRoutes)}")
print(f"MTB trail route descriptions len = {len(mtbTrailRouteDescriptions)}") 

# --------------------------------------------
# MongoDB Operations for deleting/inserting
# --------------------------------------------

# Initialize the TrailMongo DB using ATLAS 
trailMongoDB = MTBTrailMongoDB()
#db = trailMongoDB.get_database()

# mtb trail routes serialized as json 
newMTBTrailRoutes = trailMongoDB.serialize_mtb_trail_route_data(mtbTrailRoutes)

print("New MTB Trail Routes 0:")
print(newMTBTrailRoutes[-1])
print("\n")

print("MTB Trail Route Descriptions 0:")
print(mtbTrailRouteDescriptions[-1])
print("\n")

# This is needed when we need new INDEXES for the collections
#trailMongoDB.create_indexes()

# let's delete all records from the DB tables
trailMongoDB.delete_mtb_trail_route_data()

# insert the mtb trail routes to the mongoDB
print("Insert mtb trail routes...")
trailMongoDB.insert_mtb_trail_routes(newMTBTrailRoutes)

# insert the mtb trail route descriptions to the mongoDB
print("Insert mtb trail route descriptions...")
trailMongoDB.insert_mtb_trail_route_descriptions(newMTBTrailRoutes,
    mtbTrailRouteDescriptions)
