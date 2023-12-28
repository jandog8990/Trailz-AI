from pymongo import MongoClient
from pymongo import TEXT
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi
from dotenv import dotenv_values
from pandas import DataFrame
import json
import logging
import sys

# -----------------------------------------------------
# ---- PyMongo DB INSERT/GET/DELETE ----
# -----------------------------------------------------
class MTBTrailMongoDB:
    logging.basicConfig(filename='mtbtrailz.log', filemode='w',
        level=logging.DEBUG)
  
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
        config = dotenv_values(".env")
        URL_STRING = config["ATLAS_URI"]
        DB_NAME = config["DB_NAME"]
        print("URL_STRING = " + URL_STRING) 
        print("DB_NAME = " + DB_NAME)
        
        # connect to MongoDB client
        client = MongoClient(URL_STRING, server_api=ServerApi('1'))
        mtb_db = client[DB_NAME]
        return mtb_db

    # ------------------------------------------------
    # ----- CREATE INDEXES MTB Trail Route/Descs -----
    # ------------------------------------------------
    def create_indexes(self):
        self.DB.mtb_trail_routes.drop_indexes() 
        self.DB.mtb_trail_routes.create_index('_id')
        
        self.DB.mtb_trail_route_descriptions.drop_indexes()
        self.DB.mtb_trail_route_descriptions.create_index('_id')

    # -----------------------------------------------------
    # ---------- INSERT MTB Trail Route Tables ------------ 
    # -----------------------------------------------------
    
    def serialize_mtb_trail_route_data(self, mtbTrailRoutes):
        
        '''
        stateArea = mtbTrailRoute["trail_area"]["state"]
        stateAreaJson = json.dumps(stateArea.__dict__)
        print(stateAreaJson)
        print("\n")
        ''' 
      
        # loop through the mtb trail routes and serialize the trail area 
        for mtbTrailRoute in mtbTrailRoutes: 
            trailAreaDict = mtbTrailRoute["trail_area"]
            
            # nested loop for the serialized data
            serializedTrailArea = {} 
            for k, v in trailAreaDict.items():
                serializedList = [] 
                for val in v:
                    serializedArea = json.dumps(val.__dict__)
                    serializedList.append(serializedArea)
                serializedTrailArea[k] = serializedList 
            
            mtbTrailRoute["trail_area"] = serializedTrailArea
 
        return mtbTrailRoutes        
    
    def insert_mtb_trail_routes(self, mtbTrailRoutes):

        """
        MTB Trails Insertion into the PyMongo DB
        """
        # TODO: Surround with try catch so that we can't skip dup errors 
        try: 
            self.DB.mtb_trail_routes.insert_many(mtbTrailRoutes)
        except BulkWriteError as e:
            logging.error(e.details['writeErrors'])

    def insert_mtb_trail_route_descriptions(self, mtbTrailRoutes, mtbTrailRouteDescriptions):
        # # insert the sample mtb trail descriptions
        # loop through list of lists and insert 
        index = 0 
        for trailRouteDescriptions in mtbTrailRouteDescriptions: 
            # if (len(trailRouteDescriptions) == 1): 
            #    print(trailRouteDescriptions[0]) 
            
            # TODO: Surround with try catch so that we can't skip dup errors 
            try: 
                self.DB.mtb_trail_route_descriptions.insert_many(trailRouteDescriptions)
            except BulkWriteError as e: 
                logging.error(e.details['writeErrors'])
            except TypeError as e:
                logging.error("New Type error:")
                logging.error(f"Inserting trail route descriptions len = {len(trailRouteDescriptions)}") 
                logging.error(f"Index = {index}") 
                trailRoute = mtbTrailRoutes[index]
                logging.error(f"Trail route = {trailRoute['route_name']}") 
            index = index + 1 
    
    def delete_mtb_trail_route_data(self):
        self.DB.mtb_trail_routes.drop()
        self.DB.mtb_trail_route_descriptions.drop()
        
    def find_mtb_trail_descriptions(self, trailIds):
        # retrieve documents for all trailIds
        data = self.DB.mtb_trail_route_descriptions.find({'mtb_trail_route_id': {'$in': trailIds}})
        return DataFrame(data)

    def find_mtb_trail_routes(self):
        # retrieve data from both the routes/descriptions tables 
        data = self.DB.mtb_trail_routes.find() 
        return DataFrame(data)  

    # method for playing with data frame data between trail route and descriptions
    def find_mtb_trail_data(self):
        # let's pull tables and collections using the route ids 
        routeDataFrame = self.find_mtb_trail_routes()
        '''
        print(f"Trail route data len = {len(routeDataFrame)}")
        print(routeDataFrame)
        print("\n")
        ''' 
        # let's pull all of the trail route ids from the route data 
        trailIds = routeDataFrame.loc[:, '_id'].tolist()
        ''' 
        print("Trail ids from routes:")
        print(trailIds)
        print("\n")
        ''' 

        # let's get the descriptions using the list of trail ids
        descDataFrame = self.find_mtb_trail_descriptions(trailIds) 
        print("Description Data Frame:") 
        print(descDataFrame.info())
        print("\n")

        '''
        df_text = descDataFrame[['text']]
        print("DF Trail Text:")
        print(df_text)
        print("\n")
        '''
        
        # let's play around and get df rows based on ids
        """
        for id in trailIds:
            descData = descDataFrame.loc[descDataFrame['mtb_trail_route_id'] == id]
            print(f"Description data for id = {id}:")
            print(f"Description data len = {len(descData)}") 
            print(descData) 
        print("\n")
        """ 

        return descDataFrame
