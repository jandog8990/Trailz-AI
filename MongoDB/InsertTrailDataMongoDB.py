import pickle
from MTBTrailMongoDB import MTBTrailMongoDB 

# --------------------------------------------
# MongoDB Insert data into the db  
# --------------------------------------------

# import data from pkl files
pklDir = "../pkl_data"
with open(pklDir+'/mtb_routes.pkl', 'rb') as f:
    mtb_routes = pickle.load(f)
with open(pklDir+'/mtb_descs.pkl', 'rb') as f:
    mtb_descs = pickle.load(f)

print(f"Routes len = {len(mtb_routes)}")
print(f"Descs len = {len(mtb_descs)}")
print("\n")

# init mongo db
trailMongoDB = MTBTrailMongoDB()

# This is needed when we need new INDEXES for the collections
#trailMongoDB.create_indexes()

# let's delete all records from the DB tables
trailMongoDB.delete_mtb_trail_route_data()

# insert the mtb trail routes to the mongoDB
trailMongoDB.insert_mtb_trail_routes(mtb_routes)

# insert the mtb trail route descriptions to the mongoDB
trailMongoDB.insert_mtb_trail_route_descriptions(mtb_descs)
