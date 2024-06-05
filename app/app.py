import streamlit as st
import streamlit.components.v1 as components
from sentence_transformers import SentenceTransformer
import pinecone
import time
from dotenv import dotenv_values
import pickle
import re
import os
import asyncio
import json
from PineConeRAGLoader import PineConeRAGLoader

# Main Trailz AI app for searching the PineCone DB for
# recommended trailz around my area

@st.cache_resource
def load_search_data():
    # create the PineCone search loader
    print("Initialize search data objects...") 
    data_loader = PineConeRAGLoader()
    data_loader.load_pinecone_index()
    data_loader.load_openai_client()
    data_loader.load_embed_model()
    data_loader.load_rag_rails() 

    return data_loader

# retrieve the final json objects (replace with MongoDB)
def run_retrieval_norag():
    # run the docs retrieval with no RAG 
    results = asyncio.run(data_loader.retrieve(query, conditions)) 

    return results 

# set the session state vars
if 'search_click' not in st.session_state:
    st.session_state.search_click = False
if 'searching' not in st.session_state:
    st.session_state.searching = False
if 'rag_query' not in st.session_state:
    st.session_state.rag_query = ""
if 'trail_content' not in st.session_state: 
    st.session_state.trail_content = ""

def run_search():
    st.session_state.search_click = True
    st.session_state.searching = True 

def enable_query():
    st.session_state.search_click = False 
    st.session_state.searching = False

# get the search loader object
data_loader = load_search_data()
trailzAIImg = os.environ["TRAILZ_AI_IMG"]

# main Trailz AI titles
st.title("Explore Your Trailz...")

# TODO: These images will be retrieved from the query to MongoDB
#img = "https://mtbproject.com/assets/photos/mtb/4525152_medium_1554328039.jpg"
img = "https://mtbproject.com/assets/photos/mtb/5962430_medium_1554390092.jpg"
#img = "https://mtbproject.com/assets/photos/mtb/598984_medium_1554221930.jpg" 

# placeholder for loading data bar
main_placeholder = st.empty()

# prompt the user for a trail recommendation query
query_label = "What type of trails are you looking for?"
query = main_placeholder.text_input(query_label, placeholder="Fast and flowy with some jumps")


# TODO: make this a geo location that gets users location
filter_container = st.container(border=True)

# difficulties
easy_label = "Easy"
intermediate_label = "Intermediate"
difficult_label = "Difficult"

# style for the text in filter and output 
#font-weight: bold; 
#margin-left: auto;
#margin-right: auto;
st.markdown("""
    <style> 
    .diff-title {
        margin-bottom: 0px; 
        font-size: 20px; 
    }
    .route-name {
        font-size: 21px; 
        margin-bottom: 0px; 
    }
    .route-details {
        font-size: 16px; 
        margin-bottom: 0px; 
    }
    .trail-image-container {
        margin-bottom: 4px; 
        width: 100%;
        height: 180px;
        display: flex; 
        justify-content: center; 
    }
    .trail-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
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
        # Need to disable button during the actual searching 
        st.button(':white[Search]', on_click=run_search, disabled=st.session_state.searching)
    user_message = st.empty()

# run the search when search button clicked
if st.session_state.search_click:
    
    if not query:
        with filter_container: 
            user_message = st.info('''
            Please enter a trail query to find your trailz.
            ''')
            time.sleep(3)
            user_message.empty()
    else:
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

        # Check that the user is not issuing the same query as their previous
        if rag_query != st.session_state.rag_query: 
            st.session_state.rag_query = rag_query 
            
            # run the PineCone and RAG model for generating trails
            rag_rails = data_loader.rag_rails
            resp = asyncio.run(rag_rails.generate_async(messages=messages))
       
            # set the trail content to show the user 
            trail_content = resp['content'] 
            st.session_state.trail_content = trail_content 
        else:
            # previous query matches current query 
            with filter_container: 
                user_message = st.info('''
                You've already run this query, please see the results below.
                ''')
                time.sleep(3)
                user_message.empty()

# Only show trail_content results if we have them 
err_md = st.empty() 
enable_query() 
if st.session_state.trail_content: 
    trail_content = st.session_state.trail_content 
    err_md.empty() 
    resp_map = json.loads(trail_content)   
       
    # need to parse both outputs
    trail_list = resp_map['trail_list']
    stream_output = resp_map['stream_output']

    # let's create the rows of columns
    num_rows = len(trail_list)
    height = 320

    # display the stream results in the recommendation section
    if data_loader.result_holder: 
        data_loader.result_holder.empty()
        with st.container():
            st.header("Trail Recommendations", divider='rainbow') 
            if stream_output == "I don't know.":
                stream_output = '''
                Sorry, I couldn't recommend any specific trailz for you.
                However, below I've found some trailz that I 
                think you might enjoy. 
                '''
            st.write(stream_output)

    # display the trail_list results in the details section 
    with st.container():
        st.header("Trail Details", divider='rainbow')
        for i in range(0, num_rows, 2): 
            # get the data from ith object
            # need: route name, trail rating, trail dist/elev,
            # trail summary, trail image
            val1 = trail_list[i]
            route_name1 = val1['route_name']
            difficulty1 = val1['trail_rating']
            average_rating1 = val1['average_rating']
            summary1 = val1['summary']
            trail_images = val1['trail_images']
            trailImage1 = trail_images[0] if (len(trail_images) > 0) else trailzAIImg 
            print(f"Trail img 1 = {trailImage1}") 
            trailStats1 = val1['trail_stats']

            # get the data from i+1th object
            if (i+1) < num_rows: 
                val2 = trail_list[i+1]
                route_name2 = val2['route_name']
                difficulty2 = val2['trail_rating']
                average_rating2 = val2['average_rating']
                summary2 = val2['summary']
                trail_images = val2['trail_images']
                trailImage2 = trail_images[0] if (len(trail_images) > 0) else trailzAIImg 
                print(f"Trail img 2 = {trailImage2}") 
                trailStats2 = val1['trail_stats']
           
            # two columns of trail details 
            cc1, cc2 = st.columns(2) 

            with st.container():    # row container 
                # column 1 trail details 
                with cc1.container(height=height):
                    st.markdown(f'<p class="route-name"><a href="#">{route_name1}</a></p>', unsafe_allow_html=True) 
                    st.markdown(f'<p class="route-details">Difficulty: {str(difficulty1)}, Rating: {str(average_rating1)}</p>', unsafe_allow_html=True) 
                    st.markdown(f"<p class='route-details'>10mi - 2,345' Up - 2,123' Down</p>", unsafe_allow_html=True) 
                    # TODO: Make this distance, elevation up/down 
                    #st.markdown(f'<p class="route-details">Trail rating: {str(average_rating1)}</p>', unsafe_allow_html=True) 
                    #st.image(img, width=320)
                    #st.image(image,use_column_width="always") 
                    st.markdown(f'<div class="trail-image-container"><a href="/trail_details" target="_self"><img src={trailImage1} class="trail-image"></a></div>', unsafe_allow_html=True) 
                    st.markdown(summary1) 
               
                # column 2 trail details (check if we are in bounds)
                if (i+1) < num_rows: 
                    with cc2.container(height=height): 
                        st.markdown(f'<p class="route-name"><a href="#">{route_name2}</a></p>', unsafe_allow_html=True) 
                        st.markdown(f'<p class="route-details">Difficulty: {str(difficulty2)}, Rating: {str(average_rating2)}</p>', unsafe_allow_html=True) 
                        st.markdown(f"<p class='route-details'>10mi - 2,345' Up - 2,123' Down</p>", unsafe_allow_html=True) 
                        # TODO: Make this distance, elevation up/down 
                        #st.markdown(f'<p class="route-details">Trail rating: {str(average_rating2)}</p>', unsafe_allow_html=True) 
                        st.markdown(f'<div class="trail-image-container"><a href="#"><img src={trailImage2} class="trail-image"></a></div>', unsafe_allow_html=True) 
                        st.markdown(summary2) 

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

