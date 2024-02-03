import streamlit as st
from pinecone import Pinecone
import time
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
from MTBLoadDataset import MTBLoadDataset 

class PineConeSearchLoader:
    def __init__(self):
        self.loadData = MTBLoadDataset()

    @st.cache_resource
    def get_pinecone_index(_self):
        # connect to the pine cone api
        config = dotenv_values(".env")
        env_key = config["PINE_CONE_ENV_KEY"]
        api_key = config["PINE_CONE_API_KEY"]
        print("Get PineCone Index:") 
        print(f"env_key = {env_key}")
        print(f"api_key = {api_key}")
        print("\n")

        # initialize pinecone, create the index
        pc = Pinecone(
            api_key=api_key
        )
        """ 
        pinecone.init(
            api_key=api_key,
            environment=env_key
        )
        """ 

        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        index = pc.Index("trailz-ai")
        return index       

    @st.cache_resource
    def load_dataset(_self):
        # load the dataset using load data object
        print("Load Dataset:") 
        return _self.loadData.load_dataset()

    def get_final_results(self, results, metadata_set):
        print("Get final results:")
        return self.loadData.get_final_results(results, metadata_set)