import numpy as np
from pinecone import Pinecone
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# connect to the pine cone api
api_key = os.environ["PINE_CONE_API_KEY"]

# initialize PineCone, create the index
pc = Pinecone(api_key=api_key)

"""
Fetch namespace names from PC index
"""
def get_namespace_names(index):
    response = index.describe_index_stats()
    return list(response['namespaces'].keys())

# migrate data from source to target
source_pinecone_index = "trailz-ai-semantic"
target_pinecone_index = "trailz-ai"

# source PineCone
source_pinecone_env = "us-west-2"
target_pinecone_env = "us-east-1"

# init the indices
source_index = pc.Index(source_pinecone_index)
target_index = pc.Index(target_pinecone_index)

# migrate data from source to target
num_dims = 1536

# get namespaces
source_namespaces = get_namespace_names(source_index)
target_namespaces = get_namespace_names(target_index)

print(f"Source index has {len(source_namespaces)} namespaces")
print(f"Target index has {len(target_namespaces)} namespaces")

# Check if all source namespaces are in the target
missing_namespaces = set(source_namespaces) - set(target_namespaces)
if missing_namespaces:
    print(f"Warning: The following namespaces are missing in the target index: {missing_namespaces}")
else:
    print("All source namespaces are present in the target index.")

# compare vector counts
for namespace in source_namespaces:
    source_count = source_index.describe_index_stats()['namespaces'][namespace]['vector_count']
    target_count = target_index.describe_index_stats()['namespaces'].get(namespace, {}).get('vector_count', 0)
    print(f"Namespace: {namespace}")
    print(f"  Source vector count: {source_count}")
    print(f"  Target vector count: {target_count}")
    if source_count != target_count:
        print(f"  Warning: Vector counts do not match for namespace {namespace}")
    print()
