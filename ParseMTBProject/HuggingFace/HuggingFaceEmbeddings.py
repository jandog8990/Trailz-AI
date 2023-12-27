from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np


# Embedding Process: OpenAI, HuggingFace Embeddings
test_file = "/home/jandogonzales/Development/Machine Learning/MTB-Trailz/OpenAIRecommendation/data/anime_with_synopsis.csv"
pd.set_option('display.max_colwidth', 100)
df = pd.read_csv(test_file)
print(f"DF shape = {df.shape}")
print(df)
print("\n")

# slice the data frame to injest subset
subdf = df.iloc[1:10]
print(f"Sub DF shape = {subdf.shape}")
print(f"Sub DF type = {type(subdf)}")
print(subdf)
print("\n")

sub_numpy = subdf.sypnopsis.to_numpy()

# import the language model from hugging face
model1 = "all-mpnet-base-v2"
model2 = "all-MiniLM-L6-v2" 
model3 = "sentence-transformers/all-MiniLM-L6-v2" 
encoder = SentenceTransformer(model2)
#vectors = encoder.encode(subdf.sypnopsis)
vectors = encoder.encode(sub_numpy)
print(f"Vectors shape = {vectors.shape}")
print(vectors)
print("\n")

# multi-dim vectors 2D, rows being the text and the
# second dim being the length of the sentences
dim = vectors.shape[1]
print(f"Vectors text shape = {dim}")
print("\n")

# VectorDatabases: Pinecone, Chroma, Milvus, FAISS Index
index = faiss.IndexFlatL2(dim)
print(index)
index.add(vectors)

# Search the vector database using search query
search_query = "Lone samurai that fights evil with special skills"
search_vec = encoder.encode(search_query)
print(f"Search vector shape = {search_vec.shape}")
print("\n")

# Update the shape to be a single array rather than numpy vec
svec = np.array(search_vec).reshape(1, -1)
print(f"New search vec shape = {svec.shape}")
print("\n")

# search the for the query
distances, ix = index.search(svec, k=3)
print("Search res:")
print(ix)
print(distances)
print("\n")

# data frame indexing using search 
print("Query results:")
results = subdf.loc[ix[0]]
print(results.sypnopsis)
print("\n")

search_query = "Rocky and flowy trail with jumps and drops"
search_vec = encoder.encode(search_query)
svec = np.array(search_vec).reshape(1, -1)
distances, ix = index.search(svec, k=2)
print("Search res:")
print(ix)
print(distances)
print("\n")

# data frame indexing using search 
print("Query results:")
results = subdf.loc[ix[0]]
print(results.sypnopsis)
print("\n")

