from pymongo import MongoClient
from pymongo import TEXT
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi
from pandas import DataFrame
import json
import sys
import os

# -----------------------------------------------------
# ---- PyMongo TRAIL DB GET METHODS ----
# -----------------------------------------------------
class TrailMongoDB:
  
    def __init__(self):
        self.DB = self.get_database()

    # -----------------------------------------------------
    # --------- PyMongo DB Connection -----------
    # -----------------------------------------------------
    # This is the main MTB Trail MongoDB class that
    # accesses the stored tables as well as inserts
    # new data from the parsing of trail json lines
    # -----------------------------------------------------

    # get the database 
    def get_database(self):
        URL_STRING = os.environ["ATLAS_URI"]
        DB_NAME = os.environ["DB_NAME"]
        
        # connect to MongoDB client
        #client = MongoClient(URL_STRING, server_api=ServerApi('1'))
        client = MongoClient(URL_STRING) 
        mtb_db = client[DB_NAME]
         
        return mtb_db

    # ------------------------------------------------
    # ----- GET MTB Trail Route/Descs -----
    # ------------------------------------------------

    # ------------------------------------------------
    # ----- Find MTB Trail Route Descriptions -----
    # ------------------------------------------------
    def find_mtb_trail_descriptions(self):
        data = self.DB.mtb_trail_route_descriptions.find()
        return list(data)
        
    def find_mtb_trail_descriptions_by_ids(self, trailIds):
        # retrieve documents for all trailIds
        data = self.DB.mtb_trail_route_descriptions.find({'mtb_trail_route_id': {'$in': trailIds}})
        return list(data)

    # ------------------------------------------------
    # ----- Find MTB Trail Routes -----
    # ------------------------------------------------
    def find_mtb_trail_routes(self):
        # retrieve data from both the routes/descriptions tables 
        data = self.DB.mtb_trail_routes.find()
        return list(data)

    def find_mtb_trail_routes_by_ids(self, ids):
        # retrieve data from both the routes/descriptions tables 
        data = self.DB.mtb_trail_routes.find({'_id': {'$in': ids}})
        return list(data)

    # ---------------------------------------------------
    # ----- Find MTB Trail Data Routes/Descriptions -----
    # ---------------------------------------------------
    # TODO: Create queries for the trail area, refs, state (this will give
    # more flexibility to the end user
    
    # method for playing with data frame data between trail route and descriptions
    def find_mtb_trail_data(self):
        # let's pull tables and collections using the route ids 
        trailRoutes = self.find_mtb_trail_routes()
        
        # let's pull all of the trail route ids from the route data 
        #trailIds = routeDataFrame.loc[:, '_id'].tolist()
        trailIds = [frame['_id'] for frame in trailRoutes] 

        # let's get the descriptions using the list of trail ids
        trailDescriptions = self.find_mtb_trail_descriptions_by_ids(trailIds) 
        return (trailRoutes, trailDescriptions)
    
    # method for getting data frames for trail routes and descriptions
    def find_mtb_trail_data_by_ids(self, ids):
        # let's pull tables and collections using the route ids 
        trailRoutes = self.find_mtb_trail_routes_by_ids(ids)

        # let's pull all of the trail route ids from the route data 
        trailIds = [frame['_id'] for frame in trailRoutes] 

        # let's get the descriptions using the list of trail ids
        trailDescriptions = self.find_mtb_trail_descriptions_by_ids(trailIds) 

        return (trailRoutes, trailDescriptions)
