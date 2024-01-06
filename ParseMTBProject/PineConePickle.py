import sys
from datasets import Dataset
from MTBTrailMongoDB import MTBTrailMongoDB 
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
import pinecone
from tqdm.auto import tqdm
import time
import pickle
import json

# query atlas for trail data
mongoDB = MTBTrailMongoDB() 
routesDF = mongoDB.find_mtb_trail_routes()
descDF = mongoDB.find_mtb_trail_descriptions()
(routeDataFrames, descDataFrames) = mongoDB.find_mtb_trail_data()
print(f"Routes list len = {len(routesDF)}")
print(f"Descs list len = {len(descDF)}")
print("\n")
print(f"Routes link size = {len(routeDataFrames)}")
print(f"Descs link size = {len(descDataFrames)}")
print("\n")

with open('mtb_routes.pkl', 'wb') as f:
    pickle.dump(routeDataFrames, f)
with open('mtb_descs.pkl', 'wb') as f:
    pickle.dump(descDataFrames, f)

