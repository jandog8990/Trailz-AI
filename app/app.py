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

# trail filter on the left panel
filters = []
location = st.sidebar.text_input("Location")
difficulty = st.sidebar.text_input("Difficulty")
rating = st.sidebar.text_input("Rating")
filters.append(location)

# placeholder for loading data bar
main_placeholder = st.empty()

# apply filters for trailz recommendation
apply_filters_clicked = st.sidebar.button("Apply")
if apply_filters_clicked:
    # load the filters for metadata parsing
    print(f"Location = {location}")
    print(f"Difficulty = {difficulty}")
    print(f"Rating = {rating}")
    print("\n")
  
    # check if we have filters and build meta query

# prompt the user for a trail recommendation query
query = main_placeholder.text_input("What type of trail are you looking for?") 
if query:
    print(f"User query: {query}")
    embed_query = model.encode(query) 

    start = time.time()
    results = index.query(vector=[embed_query.tolist()], top_k=5)
    end = time.time()
    total = end - start
    print(f"Total query time: {total}")

    final_results = data_loader.get_final_results(results) 

    # the result is an object {answer: x, sources: y}
    st.header("Recommendations:")
    #st.subheader(final_results)
    for key,val in final_results.items():
        st.subheader(key + " : " + str(val))
