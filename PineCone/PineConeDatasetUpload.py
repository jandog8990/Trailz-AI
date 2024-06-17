from pinecone import Pinecone
from tqdm.auto import tqdm
import os
import pickle
import re

# TODO: Figure out if this can be deleted

# load the data from a pickle file
pklData="../pkl_data"
with open(pklData+"/mtb_route_dataset.pkl", 'rb') as f:
    dataset = pickle.load(f)

print(f"Dataset type = {type(dataset)}")
print(f"Dataset len = {len(dataset)}")
print("\n")

# connect to the pine cone api
api_key = os.environ["PINE_CONE_API_KEY"]
index_name = os.environ["INDEX_NAME"]
print(f"api_key = {api_key}")
print(f"index_name = {index_name}")
print("\n")

# initialize pinecone, create the index
pc = Pinecone(api_key=api_key)

# create pinecone index for searching trailz ai
#pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
index = pc.Index(index_name)
print("Index:")
print(index)
print("\n")

# upset the data in batches of 100
batch_size = 100
print(f"Dataset len = {len(dataset)}")
print(f"Batch size = {batch_size}")
for i in tqdm(range(0, len(dataset), batch_size)):
    # set the end of the current batch
    i_end = i + batch_size
    if i_end > len(dataset):
        # correct if batch is beyond dataset size
        i_end = len(dataset)
    batch = dataset[i:i_end]

    # upsert the batch of mtb route data to pinecone
    index.upsert(vectors=zip(batch['_id'], batch['vector'], batch['metadata']))
