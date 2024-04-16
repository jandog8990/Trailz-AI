from pinecone import Pinecone 
from dotenv import dotenv_values

# Search the PC database Trailz-AI index by id 
# to find duplicates in the DB

# connect to the pine cone api
config = dotenv_values(".env")
env_key = config["PINE_CONE_ENV_KEY"]
api_key = config["PINE_CONE_API_KEY"]
print(f"env_key = {env_key}")
print(f"api_key = {api_key}")
print("\n")

# TODO: This needs to be renamed to MTBDatasetLoad, then create
# the actual PineConeUpload class for upserting the new_dataset

# initialize pinecone, create the index
pinecone.init(
    api_key=api_key,
    environment=env_key
)

# create pinecone index for searching trailz ai
#pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
index = pinecone.Index("trailz-ai")
print("Index:")
print(index)
print("\n")

# query the index

