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
st.title("Explore Your Trailz...")

# placeholder for loading data bar
main_placeholder = st.empty()

# prompt the user for a trail recommendation query
progress_text = ":sunglasses: Operation in progress..."
query_label = "What type of trails are you looking for?"
query = main_placeholder.text_input(query_label)


# TODO: move the trail filters to the middle panel 
# TODO: Make this a grid of selections for difficulty 
# make this a geo location that gets users location
container = st.container(border=True)

# difficulties
easy_label = "Easy"
intermediate_label = "Intermediate"
difficult_label = "Difficult"
expert_label = "Expert"

# style for the difficulty title
st.markdown("""
    <style> 
    .diff-title {
        margin-bottom: 0px; 
        font-size: 20px; 
    }
    </style>""", unsafe_allow_html=True) 

# 
with container:
    st.header("Filter Trailz")
    col1, col2 = st.columns(2, gap="small") 
    with col1: 
        loc_label = "Location" 
        location = st.text_input(loc_label, placeholder="Your city/town")
    with col2:
        diff_label = "Difficulty" 
        st.markdown('<p class="diff-title">Difficulty</p>', unsafe_allow_html=True)
        
        col11,col12 = st.columns(2, gap="small")
        col21,col22 = st.columns(2, gap="small")
        with col11: 
            easy = st.toggle(easy_label)
        with col12: 
            intermediate = st.toggle(intermediate_label)
        with col21: 
            difficult = st.toggle(difficult_label)
        with col22: 
            expert = st.toggle(expert_label)

if query:

    # get the toggle queries
    diff_arr = [] 
    if easy:
        diff_arr.append(easy_label)
    if intermediate:
        diff_arr.append(intermediate_label)
    if difficult:
        diff_arr.append(difficult_label)

    # create the conditional queries 
    loc_arr = [] 
    if location != "":
        loc_arr = location.split(',')
    
    # Create the condition dict based on fields
    if location == '' and not diff_arr:
        conditions = {} 
    elif not diff_arr: 
        conditions = {
            "areaNames": {"$in": loc_arr}
        }
    elif location == '':
        conditions = {
            "difficulty": {"$in": diff_arr}
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

    # run the PineCone and RAG model for generating trails
    resp = asyncio.run(rag_rails.generate_async(messages=messages))
    st_success = data_loader.st_success

    # get the content and response
    content = resp['content'] 
    resp_map = json.loads(content)   
       
    # need to parse both outputs
    trail_list = resp_map['trail_list']
   
    # display the results in the new container
    with st.container():
        st.header("Trail Details", divider='rainbow')
        for val in trail_list:
            st.subheader(str(val))
        time.sleep(2)
        st_success.empty()

st.components.v1.html(
    f"""
    <script>
        var elems = window.parent.document.querySelectorAll('div[class*="stTextInput"] p');
        var elem1 = Array.from(elems).find(x => x.innerText == '{query_label}');
        var elem2 = Array.from(elems).find(x => x.innerText == '{loc_label}');
        elem1.style.fontSize = '20px'; 
        elem2.style.fontSize = '20px';
    </script>
    """
)
st.components.v1.html(
    """
    <script>
        var inelems = window.parent.document.querySelectorAll('input[class*="st-ae"]');
        input_elems = Array.from(inelems);
        for(var i = 0; i < input_elems.length; i++) {
            var elem = input_elems[i]; 
            elem.style.fontSize = '18px'; 
        }
    </script>
    """
)

