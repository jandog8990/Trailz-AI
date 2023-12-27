from sentence_transformers import SentenceTransformer
from SquadDataset import SquadDataset
import pandas as pd
from datasets import Dataset
from datasets import load_dataset
import pinecone
from tqdm.auto import tqdm
import os

# Load the SQUAD dataset
squadData = SquadDataset()
dataset = squadData.loadSQUAD()
print(f"Dataset size = {len(dataset)}")
print(dataset[0])
print("\n")

# PineCone insert
env_key = "gcp-starter"
api_key = "1f85ec08-ebe8-4f10-a27a-6c10a4385d57"
pinecone.init(
    api_key=api_key,
    environment=env_key
)

# create the pincone index
#pinecone.create_index(name='squad-test', metric='euclidean', dimension=768)
index = pinecone.Index('squad-test')
print("Index:")
print(index)
print("\n")

# upsert the data in batches of 100
batch_size = 100
for i in tqdm(range(0, len(dataset), batch_size)):
    # set the end of the current batch
    i_end = i + batch_size
    if i_end > len(dataset):
        # correct if batch is beyond dataset size
        i_end = len(dataset)
    batch = dataset[i:i_end]

    # upsert the batch to the db
    index.upsert(vectors=zip(batch['id'], batch['vector'], batch['metadata']))
