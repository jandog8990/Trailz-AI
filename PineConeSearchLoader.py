import pinecone
import time
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
from MTBLoadDataset import MTBLoadDataset 

class PineConeSearchLoader:
    def __init__(self):
        self.loadData = MTBLoadDataset()

    def get_pinecone_index(self):
        # connect to the pine cone api
        config = dotenv_values(".env")
        env_key = config["PINE_CONE_ENV_KEY"]
        api_key = config["PINE_CONE_API_KEY"]
        print(f"env_key = {env_key}")
        print(f"api_key = {api_key}")
        print("\n")

        # initialize pinecone, create the index
        pinecone.init(
            api_key=api_key,
            environment=env_key
        )

        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        index = pinecone.Index("trailz-ai")
        print("Index:")
        print(index)
        print("\n")
        return index       


