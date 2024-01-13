import streamlit as st
from sentence_transformers import SentenceTransformer
import pinecone
import time
from dotenv import dotenv_values
import pickle
import re

#Main Trailz AI app for searching the PineCone DB for
#recommended trailz around my area

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
    
# prompt the user for a trail recommendation query
query = main_placeholder.text_input("What type of trail are you looking for?") 
if query:
    print(f"User query: {query}")
   
    # the result is an object {answer: x, sources: y}
    st.header("Recommendations:")
    st.subheader("answer")
