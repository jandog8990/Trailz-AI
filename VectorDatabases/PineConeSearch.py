from sentence_transformers import SentenceTransformer

# let's use the HuggingFace multilingual library for sentence
# transformation using multiple langs
# https://huggingface.co/sentence-transformers/stsb-xlm-r-multilingual
sent = "Early engineering courses provided by American Universities in the 1870s."
model = SentenceTransformer('stsb-xlm-r-multilingual')
embeddings = model.encode(sent)

