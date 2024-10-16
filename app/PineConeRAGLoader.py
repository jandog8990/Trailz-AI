import streamlit as st
from pinecone import Pinecone
import time
import json
import base64
import os
from openai import OpenAI
from semantic_router.encoders import OpenAIEncoder
from RAGUtility import RAGUtility
from nemoguardrails import LLMRails, RailsConfig

# Loads all necessary objects for PineCone and RAG
class PineConeRAGLoader:
    def __init__(self):
        print("PineConeRAGLoader.init()...") 
        self.ragUtility = RAGUtility() 
        self.metadataSet = None
        self.rag_rails = None 
        self.index = None
        self.encoder = None
        with open("media/hackbird.GIF", "rb") as f:
            hack = f.read()
        hack_url = base64.b64encode(hack).decode("utf-8")
        self.hack_gif = f'<img src="data:image/gif;base64,{hack_url}" alt="hack gif">'
    
    @st.cache_resource
    def load_encoder(_self):
        # create the embedding transformer
        print("Loading encoder...") 
        encoder_id = os.environ["ENCODER_ID"] 
        _self.encoder = OpenAIEncoder(name=encoder_id) 
        print(_self.encoder)
        print("\n")
        
    @st.cache_resource
    def load_openai_client(_self):
        print("Loading OpenAI client...") 
        openai_api_key = os.environ["OPENAI_API_KEY"]
        _self.client = OpenAI(api_key=openai_api_key)
        print("OpenAI client:")
        print("openai api key = " + openai_api_key)
        print(_self.client)
        print("\n")
         
    @st.cache_resource
    def load_pinecone_index(_self):
        # connect to the pine cone api
        print("Loading PineCone index...") 
        api_key = os.environ["PINE_CONE_API_KEY"]
        pc_index_name = os.environ["PC_INDEX_NAME"]

        # initialize pinecone, create the index
        pc = Pinecone(
            api_key=api_key
        )
        print("Pine cone index:")
        print("api key = " + api_key)
        print(pc)
        print("\n")
         
        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        _self.index = pc.Index(pc_index_name)

    def load_retrieve_markdown(self):
        load_txt = '<span style="font-size:20px;color: #32CD32;">  Finding your trailz...</span>'
        return self.hack_gif+load_txt
    
    def load_rag_markdown(self):
        load_txt = '<span style="font-size:20px;color: #32CD32;">  Creating trail recommendations...</span>'
        return self.hack_gif+load_txt

    def stream_chunks(self, stream):
        count = 0 

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None: 
                count = count + 1 
                yield content

    # create trail contexts for OpenAI chat model
    def create_trail_contexts(self, trail_metadata):
        contexts = []
        for trail in trail_metadata:
            content = trail['content']
            route_name = trail['route_name']
            pre_id = trail['prechunk_id']
            post_id = trail['postchunk_id']
            
            # combine pre/post chunks to form context
            try:
                other_chunks = self.index.fetch(ids=[pre_id, post_id])["vectors"]
                prechunk = other_chunks[pre_id]["metadata"]["content"]
                postchunk = other_chunks[post_id]["metadata"]["content"]
                context = f"""# {route_name}

                {prechunk[-500:]}
                {content}
                {postchunk[:500]}\n"""
            except Exception as e:
                context = f"""# {route_name}

                {content}\n"""
            contexts.append(context)
    
        return contexts

    # create trail ids using the matches from vector db
    def create_trail_ids(self, trail_metadata):
        trail_ids = set()
        for meta in trail_metadata:
            trail_ids.add(meta["route_id"])
        
        return list(trail_ids) 
    
    # retrieve data from PC index using encoder 
    async def retrieve(self, query: str, conditions: str): #-> (list, list):
        # NOTE: The query and conditions are passed as json role objects
        self.md_obj = st.empty() 
        self.md_obj.markdown(self.load_retrieve_markdown(), unsafe_allow_html=True)

        print("PineCone retrieve:")
        
        # retrieve from PineCone using encoded query
        cond_dict = json.loads(conditions) 
        encoded_query = self.encoder([query])[0] 

        # issue query to PC to get context vectors
        # include_metadata=True 
        if not cond_dict:
            results = self.index.query(
                vector=encoded_query,
                top_k=12,
                include_metadata=True)
        else:
            results = self.index.query(
                vector=encoded_query,
                top_k=12,
                filter=cond_dict,
                include_metadata=True)
        print("results:")
        print(results)
        print("\n")
        
        # from the result matches create the trail meta 
        matches = results['matches'] 
        trail_metadata = [trail['metadata'] for trail in matches] 
        trail_ids = self.create_trail_ids(trail_metadata)
        
        # create trail contexts for the open ai model
        contexts = self.create_trail_contexts(trail_metadata)
        
        # returns a tuple of contexts and trail data 
        trail_list = self.ragUtility.query_trail_list(trail_ids)
        self.md_obj.empty()

        return (contexts, trail_list)

    # rag function taht receives context from PC and 
    # queries user query from open ai model
    async def rag(self, query: str, trail_tuple: tuple): #-> (str, list):
        openai_model_id = os.environ["OPENAI_MODEL_ID"]

        contexts = trail_tuple[0]
        trail_list = trail_tuple[1]
        context_str = "\n".join(contexts)

        if len(trail_list) == 0:
            stream_output = "No trailz found."
        else:
            # place the user query and contexts into RAG prompt
            self.md_obj.markdown(self.load_rag_markdown(), unsafe_allow_html=True)
            system_msg = "You are a helpful assistant."
            user_msg = f"""
            Given the following trail descriptions, please provide trail recommendations for the prompt.

            Trail Descriptions: {context_str}

            Prompt: {query}
            """
           
            # create the messages to send
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]

            # generate the RAG client completions (0.7 could be too high) 
            stream = self.client.chat.completions.create(
                model=openai_model_id,
                messages=messages,
                temperature=0.7,
                stream=True,
                max_tokens=500)
           
            # show the results from the RAG response using Stream 
            result_holder = st.empty() 
            with result_holder.container(): 
                st.header("Trail Recommendations", divider='rainbow')
                stream_output = st.write_stream(self.stream_chunks(stream))
                self.md_obj.empty()
            result_holder.empty()

        # TODO: Update this with ordering the trail list from mtb trail creator
        sortedTrailMap = self.ragUtility.sort_trail_map(trail_list, stream_output); 
        
        # return the trail list from the PineCone query and RAG output 
        bot_answer = {
            'trail_map': sortedTrailMap, 
            'stream_output': stream_output
        }

        return json.dumps(bot_answer) 
    
    @st.cache_resource
    def load_llm_rails(_self):

        print("Loading RAG rails...") 
        #import asyncio 
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)

        # create the rails using config
        railsConfig = RailsConfig.from_path("./config")
        #print("Rails config:")
        #print(railsConfig)
        #print("\n")
        
        print("Creating LLM Rails...") 
        _self.rag_rails = LLMRails(config=railsConfig) 
        print("Rag rails created...") 
        _self.rag_rails.register_action(action=_self.retrieve, name="retrieve")
        _self.rag_rails.register_action(action=_self.rag, name="rag")
        print("LLM rails actions registered...") 
        #_self.rag_rails = LLMRails(config=railsConfig, llm=_self.client, verbose=True)
        #_self.rag_rails = rag_rails
        print(_self.rag_rails) 
        print("\n")
        
    #@st.cache_resource
    def register_llm_rails_actions(_self):
        # register the actions in RAG rails obj
        print("Registering LLM Rails actions...") 
        _self.rag_rails.register_action(action=_self.retrieve, name="retrieve")
        _self.rag_rails.register_action(action=_self.rag, name="rag")