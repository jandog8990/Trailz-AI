import pinecone

# connect to the pine cone api
env_key = os.environ["PINE_CONE_ENV_KEY"]
api_key = os.environ["PINE_CONE_API_KEY"]
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

# delete the trailz index
index.delete(delete_all=True, namespace='')
