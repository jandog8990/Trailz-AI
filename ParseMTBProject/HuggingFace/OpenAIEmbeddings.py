import streamlit as st
import pickle
import time
import langchain
from dotenv import dotenv_values
from langchain.llms import OpenAI 
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# example of streamlining chunks (summary chunks from filtered chunks)
config = dotenv_values(".env")
api_key = config['OPENAI_API_KEY']

# init the LLM
llm = OpenAI(api_key=api_key, temperature=0.9, max_tokens=500)

loaders = UnstructuredURLLoader(urls=[
    "https://www.reuters.com/markets/us/futures-advance-after-dull-week-gains-tesla-2023-09-11/",
    "https://timesofindia.indiatimes.com/auto/cars/tata-punch-icng-launched-in-india-at-rs-7-09-lakh-gets-twin-cylinder-technology/articleshow/102418402.cms?from=mdr#:~:text=Tata%20Motors%20today%20finally%20launched,Pure%2C%20Adventure%2C%20and%20Accomplished."
])
data = loaders.load()

# create recursive text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
docs = text_splitter.split_documents(data)
print(f"Text splitter document length = {len(docs)")

# create embeddings with openai and faiss 
embeddings = OpenAIEmbeddings()
vectorindex_openai = FAISS.from_documents(docs, embeddings)

# store the vector index in local pkl
embed_name = "news_faiss_embeddings"
vectorindex_openai.save_local(embed_name)

# load from local storage
persistedVectorIndex = FAISS.load_local(embed_name, embeddings)
print("Persisted Vector Index:")
print(persistedVectorIndex ) 
print("\n")

# create retrieval QA with sources chain using LLM and retriever
chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=persistedVectorIndex.as_retriever()) 
print("RAG Chain:")
print(chain)
print("\n")

# query the model
query = "What is the price of Tiago ICNG?"
langchain.debug=True
chain({"question": query}, return_only_outputs=True)

# Need the combined summary from the end of the response output


