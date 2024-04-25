import streamlit as st
from pinecone import Pinecone
import time
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
from MTBLoadDataset import MTBLoadDataset 

class PineConeRAGLoader:
    def __init__(self):
        self.loadData = MTBLoadDataset()
        self.metadataSet = None
        self.index = None
        self.model = None

    @st.cache_resource
    def load_model(_self):
        # create the embedding transformer
        _self.model = SentenceTransformer("stsb-xlm-r-multilingual")

    @st.cache_resource
    def load_pinecone_index(_self):
        # connect to the pine cone api
        config = dotenv_values(".env")
        env_key = config["PINE_CONE_ENV_KEY"]
        api_key = config["PINE_CONE_API_KEY"]

        # initialize pinecone, create the index
        pc = Pinecone(
            api_key=api_key
        )

        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        _self.index = pc.Index("trailz-ai")
        print("load pinecone index done")

    @st.cache_resource
    def load_dataset(_self):
        # load the dataset using load data object
        print("Load Dataset...")
        _self.metadataSet = _self.loadData.load_dataset()

    # retrieve data from PC index using embedding 
    async def retrieve(self, query: str, conditions: dict) -> list:
        # retrieve from PineCone using embedded query
        embed_query = self.model.encode(query) 

        # issue query to PC to get context vectors
        if not conditions:
            results = self.index.query(vector=[embed_query.tolist()], top_k=10)
        else:
            results = self.index.query(vector=[embed_query.tolist()], top_k=10, filter=conditions)

        return results

    # get the final results using mtb metadata
    def get_final_results(self, results):
        return self.loadData.get_final_results(results, self.metadataSet)
