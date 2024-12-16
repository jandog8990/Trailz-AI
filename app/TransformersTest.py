from semantic_router.encoders import OpenAIEncoder
from sentence_transformers import SentenceTransformer
import os

EMBED_MODEL_ID = os.environ["EMBED_MODEL_ID"]
ENCODER_ID = os.environ["ENCODER_ID"]
ENCODER_ID = "sangmini/msmarco-cotmae-MiniLM-L12_en-ko-ja"
#model = SentenceTransformer("sangmini/msmarco-cotmae-MiniLM-L12_en-ko-ja")
model = SentenceTransformer(ENCODER_ID)
#encoder = OpenAIEncoder(name=ENCODER_ID)
print("Model:")
print(model)
print("\n")

sentences = [
    "Steep gnarly trails with drops and jumps" 
]
embeddings = model.encode(sentences)
"""
encoded_query = encoder(["Steep gnarly trails with drops and jumps"])[0]
print("Encoded query:")
print(encoded_query)
print("\n")
"""

print("Embeddings:")
print(len(embeddings[0]))
print("\n")

#similarities = model.similarity(embeddings, embeddings)
#print(similarities.shape)
# [4, 4]
