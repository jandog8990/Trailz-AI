import os
import sys
from datasets import Dataset
import pinecone
from tqdm.auto import tqdm
import time
import pickle
import json
from semantic_router.encoders import OpenAIEncoder
from semantic_chunkers import StatisticalChunker
from semantic_chunkers.schema import Chunk
from pinecone import Pinecone

# import the MongoDB path
sys.path.append('../MongoDB')
from MTBTrailMongoDB import MTBTrailMongoDB 

# ---------------------------------------------------------
# SemanticChunking class creates the routes, descriptions 
# and metadata chunks to upload semantics to PineCone 
# ---------------------------------------------------------

# get the configuration from local env
encoder_id = os.environ["ENCODER_ID"]
api_key = os.environ["PINE_CONE_API_KEY"]
pc_index_name = os.environ["PC_INDEX_NAME"]
print(f"Encoder id = {encoder_id}")

# initialize the pinecone db, encoder and stat chunker 
encoder = OpenAIEncoder(name=encoder_id)
chunker = StatisticalChunker(encoder=encoder)
pc = Pinecone(api_key=api_key)
pc_index = pc.Index(pc_index_name)
print("PC Index:")
print(pc_index.describe_index_stats())
print("\n")

# load the data from the MongoDB
trailMongoDB = MTBTrailMongoDB()
(mtb_routes, mtb_descs) = trailMongoDB.find_mtb_trail_data()
#mtb_routes = mtb_routes[0:10]
#mtb_descs = mtb_descs[0:500]

# append to the area lists if the elements exist
def append_area_lists(areaObj, areaNames, areaRefs): 
    if 'areaName' in areaObj:
        areaNames.append(areaObj["areaName"]) 
    if 'areaRef' in areaObj:
        areaRefs.append(areaObj["areaRef"]) 
    return (areaNames, areaRefs)

# --------------------------------------------------------------------
# Create the main mtb routes objects by combining routes/descriptions
# --------------------------------------------------------------------
mainMTBRoutes = [] 
print("Create MTB Trail Routes...")
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
    descs = [desc for desc in mtb_descs if desc['mtb_trail_route_id'] == route_id]
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

# create datasets from list
mtbRouteDataset = Dataset.from_list(mainMTBRoutes)
print("\n")
print(f"MTB Route Dataset len = {len(mtbRouteDataset)}")
print("\n")

# disable stats
chunker.enable_statistics = False 
chunker.plot_chunks = False

# ---------------------------------------
# -------- Test Area Chunking -----------
# ---------------------------------------
# lets loop through content and observe shit
content = mtbRouteDataset[0]['mainText']
print("Test Dataset Content:")
print(content)
print("\n")

# go through chunker and check splits
chunks = chunker(docs=[content])
chunks = chunks[0]
print(f"Chunker output (len = {len(chunks)})")
chunker.print(chunks[:3])
print("--------------\n")
# ---------------------------------------

# -------------------------------------
# Build the metadata for each chunk
# -------------------------------------
def build_metadata_chunks(doc: dict, doc_chunks: list[Chunk]):
   
    # create the metadata fields 
    route_id = doc['_id']
    metadata = doc['metadata']
    route_name = metadata['route_name']
    route_difficulty = metadata['difficulty']
    trail_rating = metadata['trail_rating']
    average_rating = metadata['average_rating']
    num_ratings = metadata['num_ratings']
    areaNames = metadata['areaNames']
    areaRefs = metadata['areaRefs']
   
    # create the content chunks and text
    metadata_chunks = [] 
    for i, chunk in enumerate(doc_chunks): 
        # get id, previous and next chunks (context for LLM)
        chunk_id = f"{route_id}#{i}"
        prechunk_id = "" if i == 0 else f"{route_id}#{i-1}"
        postchunk_id = "" if i+1 == len(doc_chunks) else f"{route_id}#{i+1}"

        # TODO: Make changes to the LLM to pull the route_id from 
        # the returned docs from PineCone
        # create dict and append to metadata list
        metadata_chunks.append({
            "id": chunk_id,
            "route_id": route_id,
            "route_name": route_name,
            "difficulty": route_difficulty,
            "trail_rating": trail_rating,
            "average_rating": average_rating,
            "num_ratings": num_ratings,
            "areaNames": areaNames,
            "areaRefs": areaRefs,
            "prechunk_id": prechunk_id,
            "postchunk_id": postchunk_id,
            "content": chunk.content
        })

    return metadata_chunks

# ----------------------------------------------------
# -------- Loop through chunks/create vectors --------
# ----------------------------------------------------
batch_size = 100
mtbRouteSemanticDataset = []
print(f"Embedding {len(mtbRouteDataset)} chunked records using semantics...")
for doc in tqdm(mtbRouteDataset):
    # create chunks on curr doc
    content = doc['mainText']
    chunks = chunker(docs=[content])
    chunks = chunks[0] 

    # create the metadata from chunks
    metadata_chunks = build_metadata_chunks(doc=doc, doc_chunks=chunks)
    
    # loop through current chunks using batches
    for i in range(0, len(chunks), batch_size):
        # for each chunk convert to embeddings using content 
        i_end = min(len(chunks), i+batch_size)

        # get batch of data for current doc
        metadata_batch = metadata_chunks[i:i_end]
        
        # get the unique ids for each chunk in batch
        ids_batch = [m["id"] for m in metadata_batch]
       
        # get the content for the current chunk (vectors)
        content_batch = [m["content"] for m in metadata_batch]

        # embed the content batch to upload
        embeddings_batch = encoder(content_batch)
        
        pc_index.upsert(vectors=zip(ids_batch, embeddings_batch, metadata_batch))
