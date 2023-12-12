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

# let's parse the json lines file to get all trail routes
jlFile = "../mtb-project-crawler/crawler/spiders/mtbproject.jl"
#jlFile = "test.jl" 
st = time.time()
jsonLineParser = MTBJsonLineParser()
trail_urls = jsonLineParser.parse(jlFile)
et = time.time()
elapsed = et - st
print(f"Json Line Parser time = {elapsed} sec")
print(f"Trail urls len = {len(trail_urls)}")
trail_urls = trail_urls[1:10000]
print("\n")

# ----------------------------------------------------
# POOL Layer for splitting the data across multiple
# nodes, currently this is still pretty slow even
# with chunking the main list into smaller pieces
# ----------------------------------------------------

# loop through the json lines and parse each individual URL
trailUrlParser = MTBTrailUrlParser()
trailDataTuples = []
for i in range(len(trail_urls)):
    url = trail_urls[i]
    if (v := trailUrlParser.parseTrail(url)) is not None:
        trailDataTuples.append(v)

# --------------------------------------------------------
# Collect the data from multiprocessing into lists after
# parsing on multiples CPUs or Nodes
# --------------------------------------------------------

# let's get individual lists of the metadata and the descriptions separately
mtbTrailRoutes = list(zip(*trailDataTuples))[0] # list of objs
mtbTrailRouteDescriptions = list(zip(*trailDataTuples))[1] # list of lists of objs

# --------------------------------------------
# MongoDB Operations for deleting/inserting
# --------------------------------------------

# Initialize the TrailMongo DB using ATLAS 
trailMongoDB = MTBTrailMongoDB()
#db = trailMongoDB.get_database()

# This is needed when we need new INDEXES for the collections
trailMongoDB.create_indexes()

# let's first serialize the mtb trail route data so that it can be inserted
newMTBTrailRoutes = trailMongoDB.serialize_mtb_trail_route_data(mtbTrailRoutes)

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
