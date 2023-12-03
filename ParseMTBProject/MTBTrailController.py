from MTBTrailUrlParser import MTBTrailUrlParser
from MTBJsonLineParser import MTBJsonLineParser
from MTBTrailMongoDB import MTBTrailMongoDB

# This is the main mtb trails parser that uses the following files:
# 1. MTBJsonLineParser.py - parses the json lines file
# 2. MTBTrailUrlParser.py - parses each individual URL
# 2. MTBTrailParser.py - parses the actual trail html page

# method for playing with data frame data between trail route and descriptions
def find_mtb_trail_data(db):
    # let's pull tables and collections using the route ids 
    routeDataFrame = trailMongoDB.find_mtb_trail_data(db)
    print(f"Trail route data len = {len(routeDataFrame)}")
    print(routeDataFrame)
    print("\n")

    # let's pull all of the trail route ids from the route data 
    trailIds = routeDataFrame.loc[:, '_id'].tolist()
    print("Trail ids from routes:")
    print(trailIds)
    print("\n")

    # let's get the descriptions using the list of trail ids
    descDataFrame = trailMongoDB.find_mtb_trail_descriptions(db, trailIds) 
    print(descDataFrame)
    print("\n")

    # let's play around and get df rows based on ids
    for id in trailIds:
        descData = descDataFrame.loc[descDataFrame['mtb_trail_route_id'] == id]
        print(f"Description data for id = {id}:")
        print(f"Description data len = {len(descData)}") 
        print(descData) 
    print("\n")

# TODO: Need to loop through the json lines file and start parsing url pages
# let's parse the json lines file to get all trail routes
jlFile = "../mtb-project-crawler/crawler/spiders/mtbproject.jl"
#jlFile = "test.jl" 
jsonLineParser = MTBJsonLineParser()
trail_urls = jsonLineParser.parse(jlFile)
print(f"Trail urls len = {len(trail_urls)}")

# loop through the json lines and parse each individual URL
trailUrlParser = MTBTrailUrlParser()
trailDataTuples = []
for i in range(len(trail_urls)):
    url = trail_urls[i]
    # TODO: Need to handle empty tuples 
    if (v := trailUrlParser.parseTrail(url)) is not None:
        trailDataTuples.append(v)

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
print("First element in the descriptions:")
print(f"First descs len = {len(mtbTrailRouteDescriptions[0])}")
print(mtbTrailRouteDescriptions[0])
print("\n")

# let's delete all records from the DB tables
trailMongoDB.delete_mtb_trail_route_data(db)

# insert the mtb trail routes to the mongoDB
trailMongoDB.insert_mtb_trail_routes(db, newMTBTrailRoutes)

# insert the mtb trail route descriptions to the mongoDB
trailMongoDB.insert_mtb_trail_route_descriptions(db, mtbTrailRouteDescriptions)

# play around with data
find_mtb_trail_data(db)