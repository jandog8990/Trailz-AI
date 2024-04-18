import streamlit as st
from sentence_transformers import SentenceTransformer
import pinecone
import time
from dotenv import dotenv_values
import pickle
import re

from PineConeSearchLoader import PineConeSearchLoader

#Main Trailz AI app for searching the PineCone DB for
#recommended trailz around my area

@st.cache_resource
def get_model():
    # create the embedding transformer
    return SentenceTransformer("stsb-xlm-r-multilingual")
    #model = SentenceTransformer("all-MiniLM-L12-v2")

@st.cache_resource
def load_search_data():
    # create the PineCone search loader
    data_loader = PineConeSearchLoader()
    index = data_loader.get_pinecone_index()
    data_loader.load_dataset()

    return (index, data_loader)

# get the transformer model and search loader
model = get_model()
(index, data_loader) = load_search_data()

# main Trailz AI titles
st.title("Trailz AI Recommendation")
st.sidebar.title("Trail Filtering")

# TODO: Move these filters to the center window for better clarity
# trail filter on the left panel
filters = []
# make this a geo location that gets users location
location = st.sidebar.text_input("Location", placeholder="Your city/town")
# TODO: Make this a grid of selections for difficulty 
difficulty = st.sidebar.text_input("Difficulty", placeholder="Easy,Intermediate,Difficult")
rating = st.sidebar.text_input("Rating", placeholder=4.1)
#filters.append(location)
#filters.append(difficulty)
#filters.append(rating)

# placeholder for loading data bar
main_placeholder = st.empty()

# prompt the user for a trail recommendation query
query = main_placeholder.text_input("What type of trail are you looking for?") 
if query:
    
    # create the conditional queries 
    diff_arr = [] 
    if difficulty != "": 
        diff_arr = difficulty.split(',') 
 
    # Create the condition dict based on fields
    if location == '' and not diff_arr and rating == '':
        conditions = {} 
    elif not diff_arr and rating == '': 
        conditions = {
            "areaNames": {"$in": [location]}
        }
    elif not diff_arr: 
        conditions = {
            "areaNames": {"$in": [location]},
            "average_rating": {"$gte": float(rating)}
        }
    else: 
        conditions = {
            "areaNames": {"$in": [location]},
            "difficulty": {"$in": diff_arr},
            "average_rating": {"$gte": float(rating)}
        }

    embed_query = model.encode(query) 

    start = time.time()
    if not conditions: 
        results = index.query(vector=[embed_query.tolist()], top_k=10) 
    else: 
        results = index.query(vector=[embed_query.tolist()], top_k=10, filter=conditions)
    end = time.time()
    total = end - start

    final_results = data_loader.get_final_results(results)
    final_results = dict(sorted(data_loader.get_final_results(results).items(), key=lambda x: x[1]['metadata']['average_rating'], reverse=True)) 

    # the result is an object {answer: x, sources: y}
    st.header("Recommendations:")
    #st.subheader(final_results)
    for key,val in final_results.items():
        st.subheader(key + " : " + str(val))
