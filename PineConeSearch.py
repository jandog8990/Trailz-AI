from sentence_transformers import SentenceTransformer
import pinecone
import time
from dotenv import dotenv_values
import pickle
import re

# open the dataset from pkl to get results
with open('pkl_data/mtb_route_dataset.pkl', 'rb') as f:
    dataset = pickle.load(f)

# dataset map updating the _id 
def update_id(objId): 
    newId = re.sub(r'[^a-zA-Z0-9\s]+', '', objId)
    newId = re.sub(' +', ' ', newId)
    newId = newId.replace(u'\xa0', u' ') 
    return newId

# create ids from the pinecone results
def create_ids(results):
    ids = [obj['id'] for obj in results['matches']]
    print(f"Ids len = {len(ids)}")
    print(ids)
    print("\n")
    return ids

# get samples from the main dataset
def get_samples(dataset):
    return {
        data['_id']: {
            'mainText': data['mainText'],
            'metadata': data['metadata']
        } for data in dataset}

# update the dataset ids
new_dataset = dataset.map(
    lambda x: {
        '_id': update_id(x['_id'])
    })

# show results from query
dataset_samples = get_samples(new_dataset)
def show_results(results):
    ids = create_ids(results)
    for i in ids:
        print(f"Result[{i}]:")
        print(dataset_samples[i])
        print("\n")

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

# create the embedder for the query
search_query = "Intermediate and difficult trails in Albuquerque and Denver" 
model = SentenceTransformer("stsb-xlm-r-multilingual")
query = model.encode(search_query)

# run the query for the trail
start = time.time()
results = index.query(vector=[query.tolist()], top_k=5)
end = time.time()
total = end - start

# load the query squad dataset
print("Results from top 5 regular query:")
show_results(results)
print("\n")

# filter using conditions for metadata
#    "average_rating": {"$gte": 4.0} 
conditions = {
    "areaNames": {"$in": ["New Mexico", "Colorado"]},
}
meta_results = index.query(vector=[query.tolist()], top_k=5, filter=conditions)
print("Results from top 5 conditional query:")
show_results(meta_results)
print("\n")
