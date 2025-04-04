from pinecone import Pinecone
from RAGUtility import RAGUtility
from models.TrailSummary import TrailSummary 
import json
import base64
import os
import streamlit as st
from semantic_router.encoders import OpenAIEncoder
from guardrails import Guard
from guardrails.hub import ToxicLanguage, SensitiveTopic 
from huggingface_hub import InferenceClient

# Loads all necessary objects for PineCone and RAG
class PineConeRAGLoader:
    def __init__(self):
        print("PineConeRAGLoader.init()...") 
        self.ragUtility = RAGUtility() 
        self.metadataSet = None
        self.index = None
        self.encoder = None
        self.input_guard = None
        self.llm_guard = None
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
    def load_hugging_face_client(_self):
        print("Loading HuggingFace client...") 
        hf_token = os.environ["HUGGING_FACE_TOKEN"]
        _self.client = InferenceClient(token=hf_token) 
 
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
        _self.llm_guard = Guard().for_pydantic(output_class=TrailSummary)

    def load_retrieve_markdown(self):
        load_txt = '<span style="font-size:20px;color: #32CD32;">  Finding your trailz...</span>'
        return self.hack_gif+load_txt
    
    def load_rag_markdown(self):
        load_txt = '<span style="font-size:20px;color: #32CD32;">  Creating trail recommendations...</span>'
        return self.hack_gif+load_txt

    def stream_chunks(self, stream):
        count = 0 
        trailzList = [] 
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
                prechunk = ""
                postchunk = "" 
                if pre_id:
                    pre_vectors = self.index.fetch([pre_id])["vectors"]
                    prechunk = pre_vectors[pre_id]["metadata"]["content"]
                if post_id:
                    post_vectors = self.index.fetch([post_id])["vectors"]
                    postchunk = post_vectors[post_id]["metadata"]["content"]
                
                # create the context from chunks and content 
                context = "" 
                if prechunk and postchunk: 
                    context = f"""# {route_name}

                    {prechunk[-500:]}
                    {content}
                    {postchunk[:500]}\n"""
                elif prechunk and not postchunk:
                    context = f"""# {route_name}

                    {prechunk[-500:]}
                    {content}\n"""
                elif postchunk and not prechunk:
                    context = f"""# {route_name}

                    {content}
                    {postchunk[:500]}\n"""
                else:
                    context = f"""# {route_name}

                    {content}\n"""
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
            return validQuery 
        except Exception as e:
            print("Validate query exception: ", e) 
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
        if not cond_dict:
            results = self.index.query(
                vector=encoded_query,
                top_k=15,
                include_metadata=True)
        else:
            results = self.index.query(
                vector=encoded_query,
                top_k=15,
                filter=cond_dict,
                include_metadata=True)

        # from the result matches create the trail meta 
        matches = results['matches'] 
        trail_metadata = [trail['metadata'] for trail in matches] 
        trail_ids = self.create_trail_ids(trail_metadata)
      
        # create the trail tuples using queries 
        trailTuple = () 
        if trail_ids: 
            # create trail contexts and trail list for the open ai model
            contexts = self.create_trail_contexts(trail_metadata)
            trail_list = self.ragUtility.query_trail_list(trail_ids)
            trailTuple = (contexts, trail_list)
            
        self.md_obj.empty()
        return trailTuple 

    # The rag() method takes the query from the messages, and the (contexts, trail_list)
    # tuple from the retrieve() method in order to call the LLM rag function 
    async def rag(self, query: str, trail_tuple: tuple): #-> (str, list):
        llama_model_id = os.environ["LLAMA_MODEL_ID"]
        contexts = trail_tuple[0]
        trail_list = trail_tuple[1]
        context_str = "\n".join(contexts)

        if len(trail_list) == 0:
            stream_output = "No trailz found."
            sortedTrailMap = {} 
        else:
            # place the user query and contexts into RAG prompt
            self.md_obj.markdown(self.load_rag_markdown(), unsafe_allow_html=True)
            system_msg = "You are a helpful trail assistant."

            # create the user message for the openai client
            user_msg = f"""
            Given the following trail descriptions, please provide a list of detailed trail recommendations, that includes 
            location, difficulty and detailed feature descriptions for each trail. 

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
                model=llama_model_id,
                messages=messages,
                temperature=0.6,
                max_tokens=600,
                stream=True)
 
            # show the results from the RAG response using Stream 
            result_holder = st.empty() 
            with result_holder.container(): 
                st.header("Trail Recommendations", divider='rainbow')
                stream_output = st.write_stream(self.stream_chunks(stream))
                self.md_obj.empty()
            result_holder.empty()

            # sort the stream output into a hashmap
            sortedTrailMap = self.ragUtility.sort_trail_map(trail_list, stream_output); 
 
        # return the trail list from the PineCone query and RAG output 
        bot_answer = {
            'trail_map': sortedTrailMap, 
            'stream_output': stream_output
        }

        return json.dumps(bot_answer) 