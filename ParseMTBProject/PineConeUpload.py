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

#TODO: We need to create a mapping of metadata to text
# 1. Create a map of ids to multiple description objects
combinedRoutes = [] 
count = 0
for route in routeDataFrames:
    # create the new route object from route and desc 
    newRouteObj = {} 
    route_id = route['_id'] 
    newRouteObj['_id'] = route_id 
    newRouteObj['trail_url'] = route['trail_url'] 
    newRouteObj['route_name'] = route['route_name'] 
    newRouteObj['difficulty'] = route['route_name'] 
    newRouteObj['average_rating'] = route['average_rating'] 
    newRouteObj['num_ratings'] = route['num_ratings'] 
   
    # parse out the state from trail area 
    trailArea = route['trail_area'] 
    st = json.loads(trailArea['state'][0])
    state = st["areaName"] 
   
    # parse out trail system from area
    st = json.loads(trailArea['trail_system'][0]) if 'trail_system' in trailArea and (len(trailArea['trail_system']) != 0) else {} 
    trailSystem = st["areaName"] if 'areaName' in st else "" 
    
    # parse out sub area from area
    st = json.loads(trailArea['sub_area'][0]) if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0) else {} 
    subArea = st["areaName"] if 'areaName' in st else "" 
    
    print(f"State = {state}")
    print(f"Trail system = {trailSystem}")
    print(f"Sub area = {subArea}")

    # create the location string from trail area  
    trailLocation = "This trail is in the state of {}.".format(state)
    if trailSystem != "":
        trailLocation = trailLocation + " In the city/town of {}.".format(trailSystem)
    if subArea != "":
        trailLocation = trailLocation + " In the area of {}.".format(subArea)
    print(f"Trail location = {trailLocation}") 
    print("\n")

    descs = [desc for desc in descDataFrames 
        if desc['mtb_trail_route_id'] == route_id]
    textArr = [desc['text'] for desc in descs] 
    mainText = "".join(textArr)
    count = count + 1
    """ 
    print(f"Route id = {route_id}")
    print(f"descs len = {len(descs)}")
    print("Route:")
    print(route)
    print("\n")
    print("Descs:")
    print(descs)
    print("\n")
    """ 
    print("Main text:")
    print(mainText)
    print("\n")
    
    if count == 2:
        break


# create datasets from lists
routesDataset = Dataset.from_list(routeDataFrames)
descsDataset = Dataset.from_list(descDataFrames)
print("First routes dataset:")
print(routesDataset[0])
print("\n")

print("First descs dataset:")
print(descsDataset[0])
print("\n")

# connect to the pine cone api
"""
config = dotenv_values(".env")
env_key = config["PINE_CONE_ENV_KEY"]
api_key = config["PINE_CONE_API_KEY"]
print(f"env_key = {env_key}")
print(f"api_key = {api_key}")
print("\n")

# initialize pinecone, create the index
pinecone.init(
    api_key=api_key,
    environment=env_key
)
pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
index = pinecone.Index("trailz-ai")
"""
