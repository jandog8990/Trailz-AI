import streamlit as st
from sentence_transformers import SentenceTransformer
import pinecone
import time
from dotenv import dotenv_values
import pickle
import re
import asyncio
import json
from PineConeRAGLoader import PineConeRAGLoader

#Main Trailz AI app for searching the PineCone DB for
#recommended trailz around my area

@st.cache_resource
def load_search_data():
    # create the PineCone search loader
    data_loader = PineConeRAGLoader()
    data_loader.load_pinecone_index()
    data_loader.load_openai_client()
    data_loader.load_embed_model()
    data_loader.ragUtility.load_dataset() 
    data_loader.load_rag_rails() 

    return data_loader

def run_retrieval_norag():
    # run the docs retrieval with no RAG 
    start = time.time()
    results = asyncio.run(data_loader.retrieve(query, conditions)) 
    end = time.time()
    total = end - start

    return sorted(data_loader.get_final_results(results).values(), key=lambda x: x['metadata']['average_rating'], reverse=True)

# get the search loader object
data_loader = load_search_data()

# main Trailz AI titles
st.title("Trailz AI Recommendation")
st.sidebar.title("Trail Filtering")

# TODO: move the trail filters to the middle panel 
# make this a geo location that gets users location
location = st.sidebar.text_input("Location", placeholder="Your city/town")
# TODO: Make this a grid of selections for difficulty 
difficulty = st.sidebar.text_input("Difficulty", placeholder="Easy,Intermediate,Difficult")

# placeholder for loading data bar
main_placeholder = st.empty()

# prompt the user for a trail recommendation query
query = main_placeholder.text_input("What type of trail are you looking for?") 
if query:
    
    # create the conditional queries 
    diff_arr = [] 
    loc_arr = [] 
    if difficulty != "": 
        diff_arr = difficulty.split(',') 
    if location != "":
        loc_arr = location.split(',')
    
    # Create the condition dict based on fields
    if location == '' and not diff_arr:
        conditions = {} 
    elif not diff_arr: 
        conditions = {
            "areaNames": {"$in": loc_arr}
        }
    else: 
        conditions = {
            "areaNames": {"$in": [location]},
            "difficulty": {"$in": diff_arr}
        }

    # get the rag rails object
    rag_rails = data_loader.rag_rails

    # create context from conditions and issue query
    cond_json = json.dumps(conditions) 

    messages = [
        {"role": "context", "content": {"conditions": cond_json}},
        {"role": "user", "content": query} 
    ]
   
    # asynchronously run rag rails query with conditions map
    resp = asyncio.run(rag_rails.generate_async(messages=messages))
    content = resp['content'] 
    resp_map = json.loads(content)   
    print(f"Ayncio Response Map:") 
    print(resp_map)
    print("\n")
   
    # need to parse both outputs
    bot_resp = resp_map['bot_str']
    trail_list = resp_map['trail_list']

    print(f"Trail results type = {type(trail_list)}")
    print(trail_list)
    print("\n")

    st.header("Trail Recommendations", divider='rainbow')
    st.subheader(bot_resp)
   
    st.header("Trail Details", divider='rainbow')
    for val in trail_list:
        st.subheader(str(val))
