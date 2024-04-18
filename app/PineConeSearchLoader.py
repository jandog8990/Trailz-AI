import streamlit as st
from pinecone import Pinecone
import time
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
from MTBLoadDataset import MTBLoadDataset 

class PineConeSearchLoader:
    def __init__(self):
        self.loadData = MTBLoadDataset()
        self.metadataSet = None
    
    @st.cache_resource
    def get_pinecone_index(_self):
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
        return pc.Index("trailz-ai")

    @st.cache_resource
    def load_dataset(_self):
        # load the dataset using load data object
        print("Load Dataset...")
        _self.metadataSet = _self.loadData.load_dataset()

    def get_final_results(self, results):
        return self.loadData.get_final_results(results, self.metadataSet)
