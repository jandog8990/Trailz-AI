import streamlit as st
from pinecone import Pinecone
import time
from openai import OpenAI
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
from MTBLoadDataset import MTBLoadDataset 

class PineConeRAGLoader:
    def __init__(self):
        self.loadData = MTBLoadDataset()
        self.config = dotenv_values(".env")
        self.metadataSet = None
        self.index = None
        self.model = None

    @st.cache_resource
    def load_embed_model(_self):
        # create the embedding transformer
        _self.model = SentenceTransformer("stsb-xlm-r-multilingual")

    @st.cache.resource
    def load_openai_client(_self):
        openai_api_key = _self.config["OPENAI_API_KEY"]
        _self.client = OpenAI(api_key=openai_api_key)

    @st.cache_resource
    def load_pinecone_index(_self):
        # connect to the pine cone api
        env_key = _self.config["PINE_CONE_ENV_KEY"]
        api_key = _self.config["PINE_CONE_API_KEY"]

        # initialize pinecone, create the index
        pc = Pinecone(
            api_key=api_key
        )

        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        _self.index = pc.Index("trailz-ai")

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

    # rag function taht receives context from PC and 
    # queries user query from open ai model
    async def rag(self, query: str, contexts: list) -> str:
        model_id = "gpt-3.5-turbo-instruct" 
        print("> RAG activated")
        context_str = "\n".join(contexts)
        print("Context str:")
        print(context_str)
        print("\n")

        # place the user query and contexts into RAG prompt
        prompt = f"""You are a helpful assistant, below is a query from a user and
        some relevant contexts. Answer the question given the information in those
        contexts. If you cannot find the answer to the question, say "I don't know".

        Contexts: {context_str}

        Query: {query}

        Answer: """

        # generate the answer
        res = self.client.completions.create(
            model=model_id,
            prompt=prompt,
            temperature=0.0,
            max_tokens=100)

        return res.choices[0].text

    # get the final results using mtb metadata
    def get_final_results(self, results):
        return self.loadData.get_final_results(results, self.metadataSet)

