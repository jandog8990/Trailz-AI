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

"""
Fetch all vector ids from given namespace in PC index

Description: Performs efficient retrieval of all vector
IDs by querying the index with random vectors and
collecting all of the matching IDs.
"""
def get_ids_from_namespace(index, namespace, num_dims, batch_size=10000):
    stats = index.describe_index_stats()
    num_vectors = stats['namespaces'].get(namespace, {}).get('vector_count', 0)
    all_ids = set()

    # loop through number of vectors in the namespace
    while len(all_ids) < num_vectors:
        input_vector = np.random.rand(num_dims).tolist()
        results = index.query(
            vector=input_vector,
            top_k=batch_size,
            namespace=namespace,
            include_values=False,
            filter={
                "id": {"$nin": list(all_ids)}   # exclude previous fetched ids
            }
        )
        new_ids = {result['id'] for result in results['matches']}
        all_ids.update(new_ids)
        print(f"Collected {len(all_ids)} ids out of {num_vectors}.")
        
        if len(new_ids) < batch_size:
            # if we received fewer results than requested, we've likely fetched all vectors
            break

    return all_ids

"""
Migrates vectors and metadata from a single namespace in the source
index to the target index. 
"""
def migrate_namespace(source_index, target_index, namespace, num_dims, batch_size=200):
    print(f'Starting migration for namespace: {namespace}')
    all_ids = get_ids_from_namespace(source_index, namespace, num_dims)
    total_vectors = len(all_ids)
    migrated_vectors = 0
    print("Migrate namespace total vectors = " + str(total_vectors))
    print("\n")

    for i in range(0, total_vectors, batch_size):
        batch_ids = list(all_ids)[i:i + batch_size]
        vectors_data = source_index.fetch(ids=batch_ids, namespace=namespace).get('vectors', {})
        vectors_to_upsert = []

        for vector_id, vector_info in vectors_data.items():
            vectors_to_upsert.append((vector_id, vector_info['values'], vector_info.get('metadata', {})))

        if vectors_to_upsert:
            batch_count = len(vectors_to_upsert)
            migrated_vectors += batch_count
            percentage_complete = (migrated_vectors / total_vectors) * 100
            print(f'Namespace {namespace}: Upserting batch of {batch_count} vectors ({migrated_vectors}/{total_vectors}, {percentage_complete:.2f}%)')
            response = target_index.upsert(vectors=vectors_to_upsert, namespace=namespace)
        else:
            print(f"No vectors found for current batch in namespace {namespace}.")

    print(f"Migration completed for namespace: {namespace}")
    return namespace, migrated_vectors

"""
Migrates all namespaces from source to target index in parallel.
"""
def parallel_migrate_namespaces(source_index, target_index, num_dims, max_workers=5):
    namespaces = get_namespace_names(source_index)
    print(f"Found {len(namespaces)} namespaces to migrate.")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_namespace = {executor.submit(migrate_namespace, source_index, target_index, namespace, num_dims): namespace for namespace in namespaces}
        for future in as_completed(future_to_namespace):
            namespace = future_to_namespace[future]
            try:
                namespace, migrated_vectors = future.result()
                print(f"Completed migration for namespace {namespace}. Migrated {migrated_vectors} vectors.")
            except Exception as exc:
                print(f"Migration for namespace {namespace} generated an exception: {exc}")

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

# execute migration
parallel_migrate_namespaces(source_index, target_index, num_dims)
print("Full migration complete.")
