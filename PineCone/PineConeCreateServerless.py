from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm
import os
import pickle
import re

# connect to the pine cone api
api_key = os.environ["PINE_CONE_API_KEY"]
print(f"api_key = {api_key}")
print("\n")

# initialize pinecone, create the index
pc = Pinecone(api_key=api_key)

# create pinecone index for searching trailz ai
#print(pc.list_indexes())
pc.create_index(name="trailz-ai",
    dimension=1536,
    metric="dotproduct",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

'''
# This is the old index
pc.create_index(name="trailz-ai-semantic",
    dimension=1536,
    metric="dotproduct",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-west-2"
    )
)
'''
print("PC:")
print(pc)

