from MTBTrailUrlParser import MTBTrailUrlParser
from MTBJsonLineParser import MTBJsonLineParser
from MTBTrailMongoDB import MTBTrailMongoDB
import multiprocessing
from multiprocessing import Pool
import numpy as np
import time
import os
import pickle

# ------------------------------------------------------------------
# This is the main mtb trails parser that uses the following files:
# 1. MTBJsonLineParser.py - parses the json lines file
# 2. MTBTrailUrlParser.py - parses each individual URL
# 3. MTBTrailParser.py - parses the actual trail html page
# ------------------------------------------------------------------

# let's parse the json lines file to get all trail routes
jlFile = "../../mtb-project-crawler/mtbproject.jl"
#jlFile = "../../mtb-project-crawler/test.jl"
st = time.time()
jsonLineParser = MTBJsonLineParser()
trailMap = jsonLineParser.parse_trailz(jlFile)
et = time.time()
elapsed = et - st
print(f"Json Line Parser time = {elapsed} sec")
print(f"Trail map len = {len(trailMap)}")
print("\n")

"""
newTrailMap = {}
count = 0
for k,v in trailMap.items():
    if count == 50:
        break
    newTrailMap[k] = v
    count += 1
"""

# ----------------------------------------------------
# Parse trail url function for parsing trail data
# ----------------------------------------------------
trailUrlParser = MTBTrailUrlParser()
def parse_trail_item(trailItem):
    return trailUrlParser.parseTrailItem(trailItem) 

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
result = pool.map_async(parse_trail_item, trailMap.items(),
        chunksize=CHUNK_LEN)
pool.close()
res = result.get()
et = time.time()
elapsed = et - st
print("\n")
print(f"CPU count = {cpu_count}")
print(f"Execution time (pooling): {elapsed} sec")
print(f"Result len = {len(res)}")

# trail data tuples
trailDataTuples = [t for t in res if t]
print(trailDataTuples)
print("\n")
print(f"Trail data tuples len = {len(trailDataTuples)}")
print("\n")

# --------------------------------------------------------
# Collect the data from multiprocessing into lists after
# parsing on multiples CPUs or Nodes
# --------------------------------------------------------

# let's get individual lists of the metadata and the descriptions separately
mtbTrailRoutes = list(zip(*trailDataTuples))[0] # list of objs
mtbTrailRouteDescriptions = list(zip(*trailDataTuples))[1] # list of lists of objs
print(f"OG MTB trail routes len = {len(mtbTrailRoutes)}")
print(f"OG MTB trail route descriptions len = {len(mtbTrailRouteDescriptions)}") 

# MTB trail route descriptions
missingIndices = [i for i in range(len(mtbTrailRouteDescriptions))
    if len(mtbTrailRouteDescriptions[i]) == 0]
missingTrailRoutes = np.take(mtbTrailRoutes, missingIndices)
print(missingIndices)
print("Missing trail data tuple 0:")
print(trailDataTuples[missingIndices[0]])
print(f"Missing indices len = {len(missingIndices)}")

# remove the missing elements
mtbTrailRouteDescriptions = [mtbTrailRouteDescriptions[i] for i in 
    range(len(mtbTrailRouteDescriptions)) if i not in missingIndices]
mtbTrailRoutes = [mtbTrailRoutes[i] for i in
    range(len(mtbTrailRoutes)) if i not in missingIndices]
print(f"MTB trail routes len = {len(mtbTrailRoutes)}")
print(f"MTB trail route descriptions len = {len(mtbTrailRouteDescriptions)}") 

# ----------------------------------------------
# Pickle Operations for inserting routes/descs
# ----------------------------------------------

# Initialize the TrailMongo DB using ATLAS 
trailMongoDB = MTBTrailMongoDB()

# mtb trail routes serialized as json 
newMTBTrailRoutes = trailMongoDB.serialize_mtb_trail_route_data(mtbTrailRoutes)
print(f"New mtb trail routes len = {len(newMTBTrailRoutes)}")

# mtb trail route descriptions unzipped
newMTBTrailRouteDescriptions = [
    desc 
    for descs in mtbTrailRouteDescriptions
    for desc in descs] 
print(f"New mtb trail route descs len = {len(newMTBTrailRouteDescriptions)}")
print("\n")

# write to pkl files
pklDir = "../pkl_data/"
with open(pklDir+"mtb_routes.pkl", 'wb') as f:
    pickle.dump(newMTBTrailRoutes, f)
with open(pklDir+"mtb_descs.pkl", 'wb') as f:
    pickle.dump(newMTBTrailRouteDescriptions, f)
