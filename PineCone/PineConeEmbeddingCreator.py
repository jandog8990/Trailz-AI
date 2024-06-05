import os
import sys
from datasets import Dataset
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
import pinecone
from tqdm.auto import tqdm
import time
import pickle
import json

# This class creates the routes, descriptions and metdata to 
# be used in a pkl file, which is then imported by
# PineConeDatasetUpload to upload to PC Index

# HuggingFace tokenizer parallelism
#os.environ["TOKENIZERS_PARALLELISM"] = "false"

# get the configuration from local env
config = dotenv_values("../.env")
embed_model_id = config["EMBED_MODEL_ID"]
print(f"Embedding model id = {embed_model_id}")
print("\n")

# load the data
pkl_data = 'pkl_data'
with open(pkl_data+'/mtb_routes.pkl', 'rb') as f:
    mtb_routes = pickle.load(f)
with open(pkl_data+'/mtb_descs.pkl', 'rb') as f:
    mtb_descs = pickle.load(f)

# append to the area lists if the elements exist
def append_area_lists(areaObj, areaNames, areaRefs): 
    if 'areaName' in areaObj:
        areaNames.append(areaObj["areaName"]) 
    if 'areaRef' in areaObj:
        areaRefs.append(areaObj["areaRef"]) 
    return (areaNames, areaRefs)

# Create the main mtb routes objects by combining routes/descriptions
mainMTBRoutes = [] 
for route in mtb_routes:
    # create the new route object from route and desc 
    newRouteObj = {} 
    route_id = route['_id'] 
    route_name = route['route_name']
    route_difficulty = route['difficulty']
    trail_rating = route['trail_rating']
    average_rating = route['average_rating']
    num_ratings = route['num_ratings']
    newRouteObj['_id'] = route_id 
    newRouteObj['trail_url'] = route['trail_url']
    newRouteObj['driving_directions'] = route['driving_directions']
    newRouteObj['gpx_file'] = route['gpx_file'] 
    newRouteObj['metadata'] = {} 
    newRouteObj['metadata']['route_name'] = route_name 
    newRouteObj['metadata']['difficulty'] = route_difficulty 
    newRouteObj['metadata']['trail_rating'] = trail_rating 
    newRouteObj['metadata']['average_rating'] = average_rating 
    newRouteObj['metadata']['num_ratings'] = num_ratings 
    
    # init the area lists 
    areaNames = [] 
    areaRefs = [] 
   
    # parse out the state from trail area 
    trailArea = route['trail_area'] 
    areaObj = json.loads(trailArea['state'][0])
    areaNames.append(areaObj["areaName"])
    areaRefs.append(areaObj["areaRef"])

    # parse out sub area from area, note that the sub-areas can have
    # multiple nested areas and sub-areas so it's best to have them all
    if 'sub_area' in trailArea and (len(trailArea['sub_area']) != 0):
        # loop through the sub areas and create array 
        areaArr = trailArea['sub_area']
        for area in areaArr:
            areaObj = json.loads(area) 
            (areaNames, areaRefs) = append_area_lists(areaObj, areaNames, areaRefs) 

    # parse out trail system from area
    areaObj = json.loads(trailArea['trail_system'][0]) if 'trail_system' in trailArea and (len(trailArea['trail_system']) != 0) else {} 
    (areaNames, areaRefs) = append_area_lists(areaObj, areaNames, areaRefs) 
  
    # NOTE: metadata queries can be used by "current" location or
    # other area prompts such as the ones used by MTBProject & AllTrails

    # set the state, city and sub areas for the metadata
    newRouteObj['metadata']['areaNames'] = areaNames 
    newRouteObj['metadata']['areaRefs'] = areaRefs 

    # need to put the trail area in a sentence description to be 
    # searched by the user query
    routeSentence = "This mtb trail route"  
    trailRouteLocation = ", ".join(areaNames) 
    trailAreaSentence = routeSentence + " is called " + route_name + ", it's located in " + trailRouteLocation + "." 

    # trail difficulty sentence
    trailDifficultySentence = routeSentence + " is rated as " + trail_rating + ", with a difficulty of " + route_difficulty + "." 
    
    # set the average rating from users
    trailUserRatingSentence = routeSentence + " has an average rider rating of " + str(average_rating) + " from " + str(num_ratings) + " different riders." 

    # create the main text from all descriptions
    descs = [desc for desc in mtb_descs 
        if desc['mtb_trail_route_id'] == route_id]
    textArr = [desc['text'] for desc in descs] 
    textArr.insert(0, trailAreaSentence)
    textArr.insert(1, trailDifficultySentence) 
    textArr.insert(2, trailUserRatingSentence) 
    mainText = " ".join(textArr)

    # remove all escape chars from description
    filter = ''.join([chr(i) for i in range(1, 32)])
    mainText = mainText.translate(str.maketrans('', '', filter))

    # create the final main text 
    newRouteObj['mainText'] = mainText 

    # append to the main routes list
    print(".", end="", flush=True) 
    mainMTBRoutes.append(newRouteObj)

# create datasets from lists
print("\n")
print(f"Main MTB Routes (len = {len(mainMTBRoutes)})")
print(mainMTBRoutes[0])
print("\n")

mtbRouteDataset = Dataset.from_list(mainMTBRoutes)
print(f"First routes dataset (len = {len(mtbRouteDataset)}):")
print(mtbRouteDataset[0])
print("\n")

# create embeddings of the main text for the mtb routes
model = SentenceTransformer(embed_model_id)

# create vector using text embeddings
mtbRouteDataset = mtbRouteDataset.map(
    lambda x: {
        'vector': model.encode(x['mainText']).tolist()
    }, batched=True, batch_size=16)

# let's save the dataset as a pkl file for use later
with open('mtb_route_dataset.pkl', 'wb') as f:
    pickle.dump(mtbRouteDataset, f)
