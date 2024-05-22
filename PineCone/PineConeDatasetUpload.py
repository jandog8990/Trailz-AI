from pinecone import Pinecone
from tqdm.auto import tqdm
import os
import pickle
from dotenv import dotenv_values
import re

route_path="app/pkl_data/"
# load the data from a pickle file
with open(route_path+'mtb_route_dataset.pkl', 'rb') as f:
    dataset = pickle.load(f)

# TODO: Will not need to update the ID since it's done in MongoDB
# dataset map updating the _id 
def update_id(objId): 
    newId = re.sub(r'[^a-zA-Z0-9\s]+', '', objId)
    newId = re.sub(' +', ' ', newId)
    newId = newId.replace(u'\xa0', u' ') 
    return newId

"""
new_dataset = dataset.map(
    lambda x: {
        '_id': update_id(x['_id'])
    })
"""

print(f"Dataset type = {type(new_dataset)}")
print("Example dataset:")
print(new_dataset[10])
print("\n")

# connect to the pine cone api
config = dotenv_values("../.env")
env_key = config["PINE_CONE_ENV_KEY"]
api_key = config["PINE_CONE_API_KEY"]
index_name = config["INDEX_NAME"]
print(f"env_key = {env_key}")
print(f"api_key = {api_key}")
print("\n")

# initialize pinecone, create the index
#    environment=env_key
pc = Pinecone(api_key=api_key)

# create pinecone index for searching trailz ai
#pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
index = pc.Index(index_name)
print("Index:")
print(index)
print("\n")

# upset the data in batches of 100
batch_size = 100
print(f"New dataset len = {len(new_dataset)}")
print(f"Batch size = {batch_size}")
for i in tqdm(range(0, len(new_dataset), batch_size)):
    # set the end of the current batch
    i_end = i + batch_size
    if i_end > len(new_dataset):
        # correct if batch is beyond new_dataset size
        i_end = len(new_dataset)
    batch = new_dataset[i:i_end]

    # upsert the batch of mtb route data to pinecone
    index.upsert(vectors=zip(batch['_id'], batch['vector'], batch['metadata']))
