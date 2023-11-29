from MTBTrailUrlParser import MTBTrailUrlParser
from MTBJsonLineParser import MTBJsonLineParser
from MTBTrailMongoDB import MTBTrailMongoDB

# This is the main mtb trails parser that uses the following files:
# 1. MTBJsonLineParser.py - parses the json lines file
# 2. MTBTrailUrlParser.py - parses each individual URL
# 2. MTBTrailParser.py - parses the actual trail html page

# TODO: Need to loop through the json lines file and start parsing url pages
# let's parse the json lines file to get all trail routes
jlFile = "../mtb-project-crawler/crawler/spiders/mtbproject.jl"
jsonLineParser = MTBJsonLineParser()
trail_urls = jsonLineParser.parse(jlFile)
print(f"Trail urls len = {len(trail_urls)}")

# loop through the json lines and parse each individual URL
trailUrlParser = MTBTrailUrlParser()
trailDataTuples = []
for i in range(5):
    url = trail_urls[i]
    trailDataTuples.append(trailUrlParser.parseTrail(url))

# TODO: Need to go through the tuples, the first element is stored as the 
# MTBTrailRoute (insertOne), and the second element is array of 
# MTBTrailRouteDescriptions (insertMany) 

# TODO: Will need to create a way to optimize the inserts as the parsing takes
# so much time that the latency could bring down the db connections

# let's get individual lists of the metadata and the descriptions separately
mtbTrailRoutes = list(zip(*trailDataTuples))[0] # list of objs
mtbTrailRouteDescriptions = list(zip(*trailDataTuples))[1] # list of lists of objs
print(f"Number of trail routes = {len(mtbTrailRoutes)}")
print(f"Number of trail route descriptions = {len(mtbTrailRouteDescriptions)}")
print(f"Trail data tuples len = {len(trailDataTuples)}")

print("Old Mtb Trail Routes:")
print(mtbTrailRoutes)
print("\n")

# at this point we issue calls to the db for insertion
trailMongoDB = MTBTrailMongoDB()
db = trailMongoDB.get_database()

# TODO: This is needed when we need new INDEXES for the collections
trailMongoDB.create_indexes(db)

# let's first serialize the mtb trail route data so that it can be inserted
newMTBTrailRoutes = trailMongoDB.serialize_mtb_trail_route_data(mtbTrailRoutes)
print(f"New Mtb Trail Routes len = {len(newMTBTrailRoutes)}")
print(newMTBTrailRoutes)
print("\n")

print(f"New Mtb Trail descriptions len = {len(mtbTrailRouteDescriptions)}")
print(mtbTrailRouteDescriptions)
print("\n")

trailMongoDB.insert_mtb_trail_routes(db, newMTBTrailRoutes)