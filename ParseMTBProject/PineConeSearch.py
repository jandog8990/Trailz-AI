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

#TODO: We need to create a mapping of metadata to text
# 1. Create a map of ids to multiple description objects
combinedRoutes = [] 
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
    st = json.loads(trailArea['state'][0])
    stateName = st["areaName"]
    stateRef = st["areaRef"]
    areaNames.append(stateName)
    areaRefs.append(stateRef)

    #TODO: Need to have this organized better
    # 1. The first element is always the State
    # 2. The last element is the actual city/location
    # 3. In between are all of the sub-areas

    # parse out sub area from area, note that the sub-areas can have
    # multiple nested areas and sub-areas so it's best to have them all
    #st = json.loads(trailArea['sub_area'][0]) if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0) else {} 
    if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0):
        
        # loop through the sub areas and create array 
        print(f"Len sub area = {len(trailArea['sub_area'])}") 
        areaArr = trailArea['sub_area']
        for area in areaArr:
            st = json.loads(area) 
            areaNames.append(st["areaName"] if 'areaName' in st else "") 
            areaRefs.append(st["areaRef"] if 'areaRef' in st else "") 

    # parse out trail system from area
    st = json.loads(trailArea['trail_system'][0]) if 'trail_system' in trailArea and (len(trailArea['trail_system']) != 0) else {} 
    cityTownName = st["areaName"] if 'areaName' in st else "" 
    cityRef = st["areaRef"]
    areaNames.append(cityTownName)
    areaRefs.append(cityRef)
  
    # metadata queries can be used by "current" location or
    # other area prompts such as the ones 
    # used by MTBProject & AllTrails
    print(f"Trail url = {route['trail_url']}")
    #print(f"State = {stateName}")
    #print(f"Trail system = {cityTownName}")
    print(f"Sub area names and refs:")
    print(areaNames)
    print(areaRefs)
    print("\n")

    # TODO: The location needs to be more consistent
    # set the state, city and sub areas for the metadata
    newRouteObj['areaNames'] = areaNames 
    newRouteObj['areaRefs'] = areaRefs 

    # need to put the trail area in a sentence description to be 
    # searched by the user query
    trailRouteName = areaNames.pop(-1)  
    trailRouteLocation = ", ".join(areaNames) 
    trailAreaSentence = "This mtb trail route lies in " + trailRouteName + " located in " + trailRouteLocation + "." 
    print("New area names:")
    print(trailAreaSentence)
    print("\n")

    # create the main text from all descriptions
    descs = [desc for desc in mtb_descs 
        if desc['mtb_trail_route_id'] == route_id]
    textArr = [desc['text'] for desc in descs] 
    textArr.insert(0, trailAreaSentence) 
    mainText = " ".join(textArr)
    count = count + 1
   
    # show the final main text
    print("Main text:")
    print(mainText)
    print("\n")
    
    if count == 5:
        break


# create datasets from lists
"""
routesDataset = Dataset.from_list(routeDataFrames)
descsDataset = Dataset.from_list(descDataFrames)
print("First routes dataset:")
print(routesDataset[0])
print("\n")

print("First descs dataset:")
print(descsDataset[0])
print("\n")
"""

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
