import streamlit as st
from pinecone import Pinecone
import json
import base64
import os
from openai import OpenAI
from semantic_router.encoders import OpenAIEncoder
from RAGUtility import RAGUtility
from guardrails import Guard
from guardrails.hub import ToxicLanguage, SensitiveTopic 
from models.TrailDetail import TrailzList

# Loads all necessary objects for PineCone and RAG
class PineConeRAGLoader:
    def __init__(self):
        print("PineConeRAGLoader.init()...") 
        self.ragUtility = RAGUtility() 
        self.metadataSet = None
        self.index = None
        self.encoder = None
        self.input_guard = None
        self.output_guard = None
        with open("media/hackbird.GIF", "rb") as f:
            hack = f.read()
        hack_url = base64.b64encode(hack).decode("utf-8")
        self.hack_gif = f'<img src="data:image/gif;base64,{hack_url}" alt="hack gif">'
    
    @st.cache_resource
    def load_encoder(_self):
        # create the embedding transformer
        encoder_id = os.environ["ENCODER_ID"] 
        _self.encoder = OpenAIEncoder(name=encoder_id) 
        
    @st.cache_resource
    def load_openai_client(_self):
        print("Loading OpenAI client...") 
        openai_api_key = os.environ["OPENAI_API_KEY"]
        _self.client = OpenAI(api_key=openai_api_key)
         
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
         
        # create pinecone index for searching trailz ai
        #pinecone.create_index(name="trailz-ai", metric="cosine", dimension=768)
        _self.index = pc.Index(pc_index_name)

    @st.cache_resource
    def load_guardrails(_self):
        print("Loading Guardrails...")
        _self.input_guard = Guard().use(
            SensitiveTopic(sensitive_topics=["politics", "sexuality", "porn", "war", "economics"],
                disable_classifier=False,
                disable_llm=False,
                on_fail="exception")
        ).use(
            ToxicLanguage(disable_classifier=False,
                disable_llm=False,
                on_fail="exception")
        ) 
        _self.output_guard = Guard().for_pydantic(output_class=TrailzList)
    
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
 
    # validate the user input using Guardrails
    def validate_query(self, query: str):
        try:
            rawQuery, validQuery, *restQuery = self.input_guard.parse(query)
            print("Valid Query:")
            print(validQuery)
            print("\n") 
       
            return validQuery 
        except Exception as e:
            raise e 
    
    # retrieve data from PC index using query and conditions from user input 
    async def retrieve(self, query: str, conditions: str): #-> (list, list):
        # NOTE: The query and conditions are passed as json role objects
        self.md_obj = st.empty() 
        self.md_obj.markdown(self.load_retrieve_markdown(), unsafe_allow_html=True)
        
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

    # NOTE: The rag() method takes the query from the messages, and the (contexts, trail_list)
    # tuple from the retrieve() method in order to call the LLM
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