import streamlit as st
import streamlit.components.v1 as components
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
    print("Initialize search data objects...") 
    data_loader = PineConeRAGLoader()
    data_loader.load_pinecone_index()
    data_loader.load_openai_client()
    data_loader.load_embed_model()
    data_loader.ragUtility.load_dataset() 
    data_loader.load_rag_rails() 

    return data_loader

# retrieve the final json objects (replace with MongoDB)
def run_retrieval_norag():
    # run the docs retrieval with no RAG 
    results = asyncio.run(data_loader.retrieve(query, conditions)) 

    return sorted(data_loader.get_final_results(results).values(), key=lambda x: x['metadata']['average_rating'], reverse=True)

# set the session state vars
if 'search_click' not in st.session_state:
    st.session_state.search_click = False
if 'rag_query' not in st.session_state:
    st.session_state.rag_query = ""
if 'trail_content' not in st.session_state: 
    st.session_state.trail_content = ""

def run_search():
    st.session_state.search_click = True

# get the search loader object
data_loader = load_search_data()

# main Trailz AI titles
st.title("Explore Your Trailz...")

# placeholder for loading data bar
main_placeholder = st.empty()

# prompt the user for a trail recommendation query
query_label = "What type of trails are you looking for?"
query = main_placeholder.text_input(query_label, placeholder="Fast and flowy with some jumps")


# TODO: Make this a grid of selections for difficulty 
# make this a geo location that gets users location
filter_container = st.container(border=True)

# difficulties
easy_label = "Easy"
intermediate_label = "Intermediate"
difficult_label = "Difficult"

# style for the text in filter and output 
st.markdown("""
    <style> 
    .diff-title {
        margin-bottom: 0px; 
        font-size: 20px; 
    }
    .route-name {
        font-size: 24px; 
        font-weight: bold; 
        margin-bottom: 0px; 
    }
    .route-details {
        font-size: 20px; 
        font-weight: 200; 
    }
    div.stButton > button:first-child {
        background-color: green;
        color: white !important; 
        border-color: black !important; 
    }
    div.stButton > button:focus{
        background-color: green;
        border-color: black !important; 
        color: white !important; 
    }
    div.stButton > button:active {
        background-color: green;
        border-color: white !important; 
        color: white !important; 
    }
    </style>""", unsafe_allow_html=True) 

# create the filter container for location and difficulty
with filter_container:
    col1, col2 = st.columns(2, gap="small") 
    col3, col4 = st.columns(2, gap="small") 
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
    with col3:
        st.button(':white[Search]', on_click=run_search)

# run the search when search button clicked
if st.session_state.search_click:
    print(f"Search clicked (and reset) = {st.session_state.search_click}")
    print(f"query = {query}")
    st.session_state.search_click = False 

    # TODO Need to store state in cache and check prev query 
    if query: 
        print(f"location = {location}") 
        print(f"easy = {easy}")
        print(f"intermediate = {intermediate}")
        print(f"difficult = {difficult}\n")

        # get the toggle queries for difficulty
        diff_arr = [] 
        if easy:
            diff_arr.append(easy_label)
        if intermediate:
            diff_arr.append(intermediate_label)
        if difficult:
            diff_arr.append(difficult_label)

        # create the conditional queries for rag query 
        loc_arr = [] 
        if location != "":
            loc_arr = location.split(',')
        
        # create the condition dict based on fields
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

        # create context from conditions and issue query
        cond_json = json.dumps(conditions) 

        messages = [
            {"role": "context", "content": {"conditions": cond_json}},
            {"role": "user", "content": query} 
        ]
        rag_query = str(messages) 
        print(f"RAG query type = {type(rag_query)}") 
        print(f"RAG query = {rag_query}") 
        print(f"Session state RAG query = {st.session_state.rag_query}\n")

        # run the PineCone and RAG model for generating trails
        if rag_query != st.session_state.rag_query: 
            print("Run RAG rails query!") 
            st.session_state.rag_query = rag_query 
            print(f"New session query = {st.session_state.rag_query}")
            rag_rails = data_loader.rag_rails
            resp = asyncio.run(rag_rails.generate_async(messages=messages))
            resp_message = data_loader.resp_message
       
            # need to make this a session state, and only update view when it's present
            trail_content = resp['content'] 
            st.session_state.trail_content = trail_content 
            print(f"Trail content type = {type(trail_content)}")
    
            # remove the success message
            if (resp_message):
                time.sleep(3)
                resp_message.empty()
                
# TODO: Need to create a state variable for changes?
# Only show results if we have them 
err_md = st.empty() 
if st.session_state.trail_content: 
    print(f"Trail content EXISTS => show results") 
    trail_content = st.session_state.trail_content 
    err_md.empty() 
    resp_map = json.loads(trail_content)   
       
    # need to parse both outputs
    trail_list = resp_map['trail_list']

    # let's create the rows of columns
    num_rows = len(trail_list)
    height = 320

    # display the results in the new container
    with st.container():
        st.header("Trail Details", divider='rainbow')
        for i in range(0, num_rows, 2): 
            # get the data from ith object
            val1 = trail_list[i]
            meta1 = val1['metadata'] 
            route_name1 = meta1['route_name']
            trail_rating1 = meta1['trail_rating']
            average_rating1 = meta1['average_rating']
            main_text1 = val1['mainText']
           
            # get the data from i+1th object
            if (i+1) < num_rows: 
                val2 = trail_list[i+1]
                meta2 = val2['metadata'] 
                route_name2 = meta2['route_name']
                trail_rating2 = meta2['trail_rating']
                average_rating2 = meta2['average_rating']
                main_text2 = val2['mainText']
           
            # two columns of trail details 
            cc1, cc2 = st.columns(2) 

            with st.container():    # row container 
                # column 1 trail details 
                with cc1.container(height=height):
                    st.markdown(f'<p class="route-name">{route_name1}</p>', unsafe_allow_html=True) 
                    st.markdown(f'<p class="route-details" style="margin-bottom: 0px;">Trail difficulty: {str(trail_rating1)}</p>', unsafe_allow_html=True) 
                    st.markdown(f'<p class="route-details">Trail rating: {str(average_rating1)}</p>', unsafe_allow_html=True) 
                    st.markdown(main_text1) 
               
                # column 2 trail details (check if we are in bounds)
                if (i+1) < num_rows: 
                    with cc2.container(height=height): 
                        st.markdown(f'<p class="route-name">{route_name2}</p>', unsafe_allow_html=True) 
                        st.markdown(f'<p class="route-details" style="margin-bottom: 0px;">Trail difficulty: {str(trail_rating2)}</p>', unsafe_allow_html=True) 
                        st.markdown(f'<p class="route-details">Trail rating: {str(average_rating2)}</p>', unsafe_allow_html=True) 
                        st.markdown(main_text2) 

components.html(
    f"""
    <script>
        var elems = window.parent.document.querySelectorAll('div[class*="stTextInput"] p');
        var elem1 = Array.from(elems).find(x => x.innerText == '{query_label}');
        var elem2 = Array.from(elems).find(x => x.innerText == '{loc_label}');
        elem1.style.fontSize = '18px'; 
        elem2.style.fontSize = '18px';
    </script>
    """
)
components.html(
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

