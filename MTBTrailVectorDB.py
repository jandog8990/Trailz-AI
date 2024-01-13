from MTBTrailMongoDB import MTBTrailMongoDB
import pandas as pd
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# init the mongo db obj
trailMongoDB = MTBTrailMongoDB()
descDF = trailMongoDB.find_mtb_trail_data()

def print_chunks(chunks):
	print(f"Total chunks = {len(chunks)}")
	for chunk in chunks:
		print(len(chunk))
	print("\n")
 
# from here need to extract text and send to vector db

# Step 1: Let's chunk this shit
# first row
mtbId = "mtb_trail_route_id"
id = "coyote/chamisoso loop"
rows = descDF.loc[descDF[mtbId].isin([id])]
rows_text = rows['text']
# df = pd.concat([rows_text['text']])
print("Row types:")
print(type(rows_text))
print(type(rows_text.values))

print("Row values:")
arr = rows_text.values
mainText = " ".join(arr)
print(type(arr))
print(arr)
print("\n")

print(mainText)
print("\n")

# use LangChain character splitter to split text
splitter = CharacterTextSplitter(
	separator="\n",
	chunk_size=200,
	chunk_overlap=0
)
chunks = splitter.split_text(mainText)

# recursive character text splitter
r_splitter = RecursiveCharacterTextSplitter(
	separators=["\n\n", "\n", " "],
	chunk_size=200,
	chunk_overlap=0
)
chunks = r_splitter.split_text(mainText)
print_chunks(chunks)

# Embedding Process: OpenAI, HuggingFace Embeddings

# VectorDatabases: Pinecone, Chroma, Milvus, FAISS Index
