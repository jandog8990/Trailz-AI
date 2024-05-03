import streamlit as st
from pinecone import Pinecone
import time
import json
import base64
from openai import OpenAI
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer
from MTBLoadDataset import MTBLoadDataset 
from RAGUtility import RAGUtility

# Loads all necessary objects for PineCone and RAG
class PineConeRAGLoader:
    def __init__(self):
        self.ragUtility = RAGUtility() 
        self.config = dotenv_values(".env")
        self.metadataSet = None
        self.rag_rails = None 
        self.index = None
        self.model = None

    @st.cache_resource
    def load_embed_model(_self):
        # create the embedding transformer
        print("Load Embed model...") 
        _self.model = SentenceTransformer("stsb-xlm-r-multilingual")

    @st.cache_resource
    def load_openai_client(_self):
        print("Load OpenAI client...") 
        openai_api_key = _self.config["OPENAI_API_KEY"]
        _self.client = OpenAI(api_key=openai_api_key)

    @st.cache_resource
    def load_pinecone_index(_self):
        # connect to the pine cone api
        print("Load PC index...") 
        env_key = _self.config["PINE_CONE_ENV_KEY"]
        api_key = _self.config["PINE_CONE_API_KEY"]

        # initialize pinecone, create the index
        pc = Pinecone(
            api_key=api_key
        )

        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        _self.index = pc.Index("trailz-ai")

    def load_markdown(self):
        with open("hackbird.GIF", "rb") as f:
            hack = f.read()
        hack_url = base64.b64encode(hack).decode("utf-8")
        hack_gif = f'<img src="data:image/gif;base64,{hack_url}" alt="hack gif">'
        load_txt = '<span style="font-size:20px;color: #32CD32;">  Finding your trailz...</span>'
        return hack_gif+load_txt

    def stream_chunks(self, stream):
        count = 0 

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None: 
                count = count + 1 
                yield content

    # retrieve data from PC index using embedding 
    async def retrieve(self, query: str, conditions: str) -> (list, list):
        # NOTE: The query and conditions are passed as json role objects

        # retrieve from PineCone using embedded query
        cond_dict = json.loads(conditions) 
        embed_query = self.model.encode(query) 

        # issue query to PC to get context vectors
        self.md_obj = st.empty() 
        self.md_obj.markdown(self.load_markdown(), unsafe_allow_html=True)
        if not cond_dict:
            results = self.index.query(vector=[embed_query.tolist()], top_k=20)
        else:
            results = self.index.query(vector=[embed_query.tolist()], top_k=20, filter=cond_dict)

        return self.ragUtility.parse_contexts(results)

    # rag function taht receives context from PC and 
    # queries user query from open ai model
    async def rag(self, query: str, trail_tuple: tuple) -> (str, list):
        #model_id = "gpt-3.5-turbo-instruct" 
        #model_id = "gpt-3.5-turbo-0125" 
        model_id = "gpt-4-turbo" 
       
        contexts = trail_tuple[0]
        trail_list = trail_tuple[1]
        context_str = "\n".join(contexts)

        # place the user query and contexts into RAG prompt
        system_msg = "You are a helpful assistant, below is a query from a user and some relevant contexts." 
        user_msg = f"""Answer the question given the information in those
        contexts. If you cannot find the answer to the question, say "I don't know".

        Contexts: {context_str}

        Query: {query}

        Answer: """
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
        
        # generate the RAG client completions 
        #NOTE: higher temp means more randomness 
        stream = self.client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.0,
            stream=True,
            max_tokens=1000)
       
        # show the results from the RAG response using Stream 
        result_holder = st.empty() 
        with result_holder.container(): 
            st.header("Trail Recommendations", divider='rainbow')
            st.write_stream(self.stream_chunks(stream))
            self.md_obj.empty()
            self.st_success = st.success('Trailz found! See below for details.')

        # return the trail list from the PineCone query 
        bot_answer = {
            'trail_list': trail_list 
        }
        
        return json.dumps(bot_answer) 
    
    @st.cache_resource
    def load_rag_rails(_self):
        import asyncio 
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        from nemoguardrails import LLMRails, RailsConfig
        import os

        print("Load RAG rails...") 
        openai_api_key = _self.config["OPENAI_API_KEY"]
        os.environ["OPENAI_API_KEY"] = openai_api_key
        (yaml_content, rag_colang_content) = _self.ragUtility.get_rag_config()

        config = RailsConfig.from_content(
            colang_content=rag_colang_content,
            yaml_content=yaml_content)

        # create the rails
        _self.rag_rails = LLMRails(config)

        # register the actions in RAG rails obj
        _self.rag_rails.register_action(action=_self.retrieve, name="retrieve")
        _self.rag_rails.register_action(action=_self.rag, name="rag")

