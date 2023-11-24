from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import dotenv_values
from pandas import DataFrame

# -----------------------------------------------------
# --------- PyMongo DB Connection -----------
# -----------------------------------------------------
# This is the main MTB Trail MongoDB class that
# accesses the stored tables as well as inserts
# new data from the parsing of trail json lines
# -----------------------------------------------------

# get the database 
def get_database():
    config = dotenv_values(".env")
    URL_STRING = config["ATLAS_URI"]
    DB_NAME = config["DB_NAME"]
    print("URL_STRING = " + URL_STRING) 
    print("DB_NAME = " + DB_NAME)
    
    # connect to MongoDB client
    client = MongoClient(URL_STRING, server_api=ServerApi('1'))
    mtb_db = client[DB_NAME]
    return mtb_db

# -----------------------------------------------------
# --------- MTB Trail Route Tables ----------- 
# -----------------------------------------------------
import json
mtb_db = get_database()

print("\n")
print("MTB Trail Route:")
stateArea = mtbTrailRoute["trail_area"]["state"]
stateAreaJson = json.dumps(stateArea.__dict__)
print(stateAreaJson)
print("\n")

trailAreaDict = mtbTrailRoute["trail_area"]
for k,v in trailAreaDict.items():
    print(f"{k} : {v}")
print("\n")

serializedTrailArea = dict((k, json.dumps(v.__dict__)) for k, v in trailAreaDict.items())
print("Serialized Trail Area:")
print(serializedTrailArea)
print("\n")

# TODO: Need to figure out how to serialize the json strings back to object space
mtbTrailRoute["trail_area"] = serializedTrailArea

print("New MTB Trail Route Serialization:")
print(mtbTrailRoute)
print("\n")

print("MTB Trail Route Descriptions:")
print(mtbTrailRouteDescriptions)
print("\n")

"""
MTB Trails Insertion into the PyMongo DB
"""
# # let's insert sample mtb trail route 
# trail_route_collection = mtb_db["mtb_trail_routes"]
# trail_route_collection.insert_one(mtbTrailRoute)

# # insert the sample mtb trail descriptions
# description_collection = mtb_db["mtb_trail_route_descriptions"]
# description_collection.insert_many(mtbTrailRouteDescriptions) 

# get the tables 
trail_routes = mtb_db["mtb_trail_routes"]
trail_descriptions = mtb_db["mtb_trail_route_descriptions"]

# query the table info
routeItems = trail_routes.find()
descItems = trail_descriptions.find()

# convert the collections to data frames
routeDF = DataFrame(routeItems)
descDF = DataFrame(descItems)

print("--- Route DF ---")
print(routeDF)
print("\n")

print("--- Desc DF ---")
print(descDF)
print("\n")