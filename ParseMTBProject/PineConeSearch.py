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

# load the data
with open('mtb_routes.pkl', 'rb') as f:
    mtb_routes = pickle.load(f)
with open('mtb_descs.pkl', 'rb') as f:
    mtb_descs = pickle.load(f)
print(f"Routes len = {len(mtb_routes)}")
print(f"Descs len = {len(mtb_descs)}")

# append to the area lists if the elements exist
def append_area_lists(areaObj, areaNames, areaRefs): 
    if 'areaName' in areaObj:
        areaNames.append(areaObj["areaName"]) 
    if 'areaRef' in areaObj:
        areaRefs.append(areaObj["areaRef"]) 
    return (areaNames, areaRefs)

#TODO: We need to create a mapping of metadata to text
# 1. Create a map of ids to multiple description objects
mainMTBRoutes = [] 
count = 0
for route in mtb_routes:
    # create the new route object from route and desc 
    newRouteObj = {} 
    route_id = route['_id'] 
    newRouteObj['_id'] = route_id 
    newRouteObj['trail_url'] = route['trail_url'] 
    newRouteObj['route_name'] = route['route_name'] 
    newRouteObj['difficulty'] = route['route_name'] 
    newRouteObj['average_rating'] = route['average_rating'] 
    newRouteObj['num_ratings'] = route['num_ratings'] 
    
    # init the area lists 
    areaNames = [] 
    areaRefs = [] 
   
    # parse out the state from trail area 
    trailArea = route['trail_area'] 
    areaObj = json.loads(trailArea['state'][0])
    areaNames.append(areaObj["areaName"])
    areaRefs.append(areaObj["areaRef"])

    #TODO: Need to have this organized better
    # 1. The first element is always the State
    # 2. The last element is the actual city/location
    # 3. In between are all of the sub-areas

    # parse out sub area from area, note that the sub-areas can have
    # multiple nested areas and sub-areas so it's best to have them all
    #st = json.loads(trailArea['sub_area'][0]) if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0) else {} 
    if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0):
        
        # loop through the sub areas and create array 
        areaArr = trailArea['sub_area']
        for area in areaArr:
            areaObj = json.loads(area) 
            (areaNames, areaRefs) = append_area_lists(areaObj, areaNames, areaRefs) 

    # parse out trail system from area
    areaObj = json.loads(trailArea['trail_system'][0]) if 'trail_system' in trailArea and (len(trailArea['trail_system']) != 0) else {} 
    (areaNames, areaRefs) = append_area_lists(areaObj, areaNames, areaRefs) 
  
    # metadata queries can be used by "current" location or
    # other area prompts such as the ones 
    # used by MTBProject & AllTrails

    # TODO: The location needs to be more consistent
    # set the state, city and sub areas for the metadata
    newRouteObj['areaNames'] = areaNames 
    newRouteObj['areaRefs'] = areaRefs 

    # need to put the trail area in a sentence description to be 
    # searched by the user query
    trailRouteName = areaNames[-1] 
    trailRouteLocation = ", ".join(areaNames) 
    trailAreaSentence = "This mtb trail route lies in " + trailRouteName + " located in " + trailRouteLocation + "." 

    # create the main text from all descriptions
    descs = [desc for desc in mtb_descs 
        if desc['mtb_trail_route_id'] == route_id]
    textArr = [desc['text'] for desc in descs] 
    textArr.insert(0, trailAreaSentence) 
    mainText = " ".join(textArr)
    count = count + 1
  
    # show the final main text
    newRouteObj['mainText'] = mainText 

    # append to the main routes list
    print(".", end="", flush=True) 
    mainMTBRoutes.append(newRouteObj)

# create datasets from lists
print(f"\nMain MTB Routes len = {len(mainMTBRoutes)}")
print(mainMTBRoutes[0:2])
print("\n")

mtbRoutesDataset = Dataset.from_list(mainMTBRoutes)
print(f"First routes dataset (len = {len(mtbRoutesDataset)}):")
print(mtbRoutesDataset[0])
print("\n")

# connect to the pine cone api
config = dotenv_values(".env")
env_key = config["PINE_CONE_ENV_KEY"]
api_key = config["PINE_CONE_API_KEY"]
print(f"env_key = {env_key}")
print(f"api_key = {api_key}")
print("\n")

# TODO: This needs to be renamed to MTBDatasetLoad, then create
# the actual PineConeUpload class for upserting the datasets

# initialize pinecone, create the index
"""
pinecone.init(
    api_key=api_key,
    environment=env_key
)
pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
index = pinecone.Index("trailz-ai")
"""
