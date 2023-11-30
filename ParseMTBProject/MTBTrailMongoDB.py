from pymongo import MongoClient
from pymongo import TEXT
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi
from dotenv import dotenv_values
from pandas import DataFrame
import json
import logging

# -----------------------------------------------------
# ---- PyMongo DB INSERT/GET/DELETE ----
# -----------------------------------------------------
class MTBTrailMongoDB:
    logging.basicConfig(filename='mtbtrailz.log', filemode='w',
        level=logging.DEBUG)
    
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
    def create_indexes(self, db):
        print("--- OLD ROUTE INDEX ---") 
        #db.mtb_trail_routes.drop_index('_id') 
        print(db.mtb_trail_routes.index_information())
        db.mtb_trail_routes.drop_indexes() 
        # db.mtb_trail_routes.create_index('route_name')
        print("--- NEW ROUTE INDEX ---") 
        print(db.mtb_trail_routes.index_information())
        
        print("--- OLD DESC INDEX ---") 
        #db.mtb_trail_route_descriptions.drop_index('_id') 
        print(db.mtb_trail_route_descriptions.index_information())
        print(db.mtb_trail_route_descriptions.drop_indexes())
        # db.mtb_trail_route_descriptions.create_index('mtb_trail_route_id')
        print("--- NEW DESC INDEX ---") 
        print(db.mtb_trail_route_descriptions.index_information())

    # -----------------------------------------------------
    # ---------- INSERT MTB Trail Route Tables ------------ 
    # -----------------------------------------------------
    
    def serialize_mtb_trail_route_data(self, mtbTrailRoutes):
        
        print("MTB Trail Route:")
        '''
        stateArea = mtbTrailRoute["trail_area"]["state"]
        stateAreaJson = json.dumps(stateArea.__dict__)
        print(stateAreaJson)
        print("\n")
        ''' 
      
        # loop through the mtb trail routes and serialize the trail area 
        for mtbTrailRoute in mtbTrailRoutes: 
            trailAreaDict = mtbTrailRoute["trail_area"]
            '''
            for k,v in trailAreaDict.items():
                print(f"{k} : {v}")
            print("\n")
            ''' 
            serializedTrailArea = dict((k, json.dumps(v.__dict__)) for k, v in trailAreaDict.items())

            # TODO: Need to figure out how to serialize the json strings back to object space
            mtbTrailRoute["trail_area"] = serializedTrailArea
        return mtbTrailRoutes        
    
    def insert_mtb_trail_routes(self, db, mtbTrailRoutes):

        """
        MTB Trails Insertion into the PyMongo DB
        """
        # TODO: Surround with try catch so that we can't skip dup errors 
        try: 
            db.mtb_trail_routes.insert_many(mtbTrailRoutes)
        except BulkWriteError as e:
            logging.error(e.details['writeErrors'])

    def insert_mtb_trail_route_descriptions(self, db, mtbTrailRouteDescriptions):
        # # insert the sample mtb trail descriptions
        # loop through list of lists and insert 
        for trailRouteDescriptions in mtbTrailRouteDescriptions: 
            # TODO: Surround with try catch so that we can't skip dup errors 
            try: 
                db.mtb_trail_route_descriptions.insert_many(trailRouteDescriptions)
            except BulkWriteError as e:
                logging.error(e.details['writeErrors'])

    def delete_mtb_trail_route_data(self, db):
        db.mtb_trail_routes.drop()
        db.mtb_trail_route_descriptions.drop()
        
    def find_mtb_trail_descriptions(self, db, trailIds):
        # retrieve documents for all trailIds
        data = db.mtb_trail_route_descriptions.find({'mtb_trail_route_id': {'$in': trailIds}})
        return DataFrame(data)

    def find_mtb_trail_data(self, db):
        # retrieve data from both the routes/descriptions tables 
        data = db.mtb_trail_routes.find() 
        return DataFrame(data)  