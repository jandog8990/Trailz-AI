import streamlit as st
import streamlit.components.v1 as components
import pinecone
import time
from dotenv import dotenv_values
import pickle
import re
import os
import asyncio
import json
from PineConeRAGLoader import PineConeRAGLoader
from TrailUtility import TrailUtility 
from streamlit_session_browser_storage import SessionStorage

# Main Trailz AI app for searching the PineCone DB for
# recommended trailz around my area

@st.cache_resource
def load_search_data():
    # create the PineCone search loader
    print("Initialize search data objects...") 
    data_loader = PineConeRAGLoader()
    data_loader.load_pinecone_index()
    data_loader.load_openai_client()
    data_loader.load_encoder()
    data_loader.load_rag_rails() 

    return data_loader

# retrieve the final json objects (replace with MongoDB)
def run_retrieval_norag():
    # run the docs retrieval with no RAG 
    results = asyncio.run(data_loader.retrieve(query, conditions)) 

    return results 

# initialize the local state 
def load_session_state():
    if 'search_click' not in st.session_state:
        st.session_state['search_click'] = False
    if 'searching' not in st.session_state:
        st.session_state['searching'] = False
    if 'rag_query' not in st.session_state:
        st.session_state['rag_query'] = ""
    if 'easy' not in st.session_state:
        st.session_state['easy'] = False 
    if 'intermediate' not in st.session_state:
        st.session_state['intermediate'] = False 
    if 'difficult' not in st.session_state:
        st.session_state['difficult'] = False 
    if 'trail_list' not in st.session_state: 
        st.session_state['trail_list'] = ""
    if 'stream_output' not in st.session_state: 
        st.session_state['stream_output'] = ""
    if 'units' not in st.session_state: 
        st.session_state['units'] = "Imperial"

# initialize the local storage if exists
def load_session_storage():
    # NOTE: Somehow parse this and communicate that we have cache?!
    # 1. Compare the new search query with the previous
    # 2. If anything exists in the session storage than show it
    # 3. Do we need to requery or have separate templates?? 
    storageContents = sessionStorage.getAll()
    if "stream_output_sesh1" in storageContents:
        st.session_state["stream_output"] = storageContents["stream_output_sesh1"]
    if "trail_list_sesh1" in storageContents:
        st.session_state["trail_list"] = storageContents["trail_list_sesh1"]
    if "query_sesh1" in storageContents:
        st.session_state["query"] = storageContents["query_sesh1"]
    if "location_sesh1" in storageContents:
        st.session_state["location"] = storageContents["location_sesh1"]
    if "rag_query_sesh1" in storageContents:
        st.session_state["rag_query"] = storageContents["rag_query_sesh1"]
    if "easy_sesh1" in storageContents:
        st.session_state["easy"] = storageContents["easy_sesh1"]
    if "intermediate_sesh1" in storageContents:
        st.session_state["intermediate"] = storageContents["intermediate_sesh1"]
    if "difficult_sesh1" in storageContents:
        st.session_state["difficult"] = storageContents["difficult_sesh1"]
    if "units_sesh1" in storageContents:
        st.session_state["units"] = storageContents["units_sesh1"]

def run_search():
    st.session_state.search_click = True
    st.session_state.searching = True 

def enable_query():
    st.session_state.search_click = False 
    st.session_state.searching = False
    
# get the search loader object
trailUtility = TrailUtility()
trailzAIImg = os.environ["TRAILZ_AI_IMG"]
load_session_state()
sessionStorage = SessionStorage()
data_loader = load_search_data()
load_session_storage()
#sessionStorage.deleteAll()

# main Trailz AI titles
st.title("Explore Your Trailz...")

# placeholder for loading data bar
main_placeholder = st.empty()

# prompt the user for a trail recommendation query
query_label = "What type of trails are you looking for?"
queryVal = st.session_state["query"] if "query" in st.session_state else ""
query = main_placeholder.text_input(query_label, value=queryVal, placeholder="Fast and flowy with some jumps")

# TODO: make this a geo location that gets users location
filter_container = st.container(border=True)

# difficulties
easy_label = "Easy"
intermediate_label = "Intermediate"
difficult_label = "Difficult"
units_label = "Units"

# ----------------------------------------
# Style for the text in filter and output 
# ----------------------------------------
st.markdown("""
    <style> 
    .toggle-title {
        margin-bottom: 0px; 
        font-size: 20px; 
    }
    div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
        margin-bottom: 0px; 
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
    div.stButton {
        margin-bottom: 4px; 
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
    col3, col4 = st.columns([1, 1]) 
    with col1: 
        loc_label = "Location" 
        locationVal = st.session_state["location"] if "location" in st.session_state else ""
        location = st.text_input(loc_label, value=locationVal, placeholder="Your city/town")
    with col2:
        diff_label = "Difficulty" 
        st.markdown('<p class="toggle-title">Difficulty</p>', unsafe_allow_html=True)
        
        col11,col12 = st.columns(2, gap="small")
        col21,col22 = st.columns(2, gap="small")
        with col11: 
            easyVal = st.session_state["easy"] if "easy" in st.session_state else False 
            easy = st.toggle(easy_label, value=easyVal)
        with col12: 
            intermediateVal = st.session_state["intermediate"] if "intermediate" in st.session_state else False 
            intermediate = st.toggle(intermediate_label, value=intermediateVal)
        with col21: 
            difficultVal = st.session_state["difficult"] if "difficult" in st.session_state else False 
            difficult = st.toggle(difficult_label, value=difficultVal)
    with col3:
        st.write("") 
        st.button(':white[Search]', on_click=run_search, disabled=st.session_state.searching)
    with col4: 
        unitsIndex = 0 if st.session_state["units"] == "Imperial" else 1
        units = st.radio("Units", ["Imperial", "Metric"], index=unitsIndex, horizontal=True)
        st.session_state.units = units
    
    user_message = st.empty()

# --------------------------------------------------------
# Run the Pinecone/RAG search when search button clicked
# --------------------------------------------------------
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
            st.session_state.easy = easy
            st.session_state.intermediate = intermediate
            st.session_state.difficult = difficult

            # run the PineCone and RAG model for generating trails
            rag_rails = data_loader.rag_rails
            resp = asyncio.run(rag_rails.generate_async(messages=messages))
       
            # set the trail content to show the user 
            trail_content = resp['content'] 
            #st.session_state.trail_content = trail_content 
        else:
            # previous query matches current query 
            trail_content = None 
            with filter_container: 
                user_message = st.info('''
                You've already run this query, please see the results below.
                ''')
                time.sleep(3)
                user_message.empty()

        # ---------------------------------------------------------
        # Parse trail_content results from the Pinecone/RAG Model 
        # ---------------------------------------------------------
        err_md = st.empty() 
        enable_query() 
        if trail_content: 
            err_md.empty() 
            try: 
                resp_map = json.loads(trail_content)   
            
                # need to parse both outputs
                trail_list = resp_map['trail_list']
                stream_output = resp_map['stream_output']
               
                # Store stream output and trail list in session state 
                st.session_state["stream_output"] = stream_output 
                st.session_state["trail_list"] = json.dumps(trail_list)
            except Exception as e:
                # TODO: When to clear the local storage? after each query? or
                # when the query changes per search?
                with filter_container: 
                    err_msg = st.error(trail_content)
                    time.sleep(6)
                    err_msg.empty()

# --------------------------------------------------------
# Results container for the stream output and trail list 
# --------------------------------------------------------
if st.session_state.trail_list: 
    stream_output = st.session_state["stream_output"]
    trail_list = json.loads(st.session_state["trail_list"])
    st.session_state["location"] = location 
    st.session_state["query"] = query 

    # let's create the rows of columns
    trail_list_len = len(trail_list)
    container_height = 320

    # display the stream results in the recommendation section
    if data_loader.result_holder: 
        data_loader.result_holder.empty()
        with st.container():
            st.header("Trail Recommendations", divider='rainbow') 
            if stream_output == "I don't know.":
                stream_output = '''
                Sorry, I couldn't recommend any specific trailz for you.
                However, below I've found some trailz that I think you 
                might enjoy. Or, you can try another search! 
                '''
            st.write(stream_output)

    # display the trail_list results in the details section 
    with st.container():
        st.header("Trail Details", divider='rainbow')
        for i in range(0, trail_list_len, 2): 
            # get the data from ith object
            # need: route name, trail rating, trail dist/elev,
            # trail summary, trail image
            val1 = trail_list[i]
            id1 = val1['_id'] 
            url1 = val1['trail_url'] 
            route_name1 = val1['route_name']
            difficulty1 = val1['trail_rating']
            average_rating1 = val1['average_rating']
            summary1 = val1['summary']
            trail_images = val1['trail_images']
            trailImage1 = trail_images[0] if (len(trail_images) > 0) else trailzAIImg 
            trailStats1 = val1['trail_stats']
            
            # use the trail utility to parse the trail stats
            routeDetails1 = trailUtility.createTrailStats(trailStats1, units) 

            # get the data from i+1th object
            if (i+1) < trail_list_len: 
                val2 = trail_list[i+1]
                id2 = val2['_id'] 
                url2 = val2['trail_url'] 
                route_name2 = val2['route_name']
                difficulty2 = val2['trail_rating']
                average_rating2 = val2['average_rating']
                summary2 = val2['summary']
                trail_images = val2['trail_images']
                trailImage2 = trail_images[0] if (len(trail_images) > 0) else trailzAIImg 
                trailStats2 = val2['trail_stats']

                # use the trail utility to parse the trail stats
                routeDetails2 = trailUtility.createTrailStats(trailStats2, units) 
           
            # two columns of trail details 
            cc1, cc2 = st.columns(2) 

            with st.container():    # row container 
                # column 1 trail details 
                # TODO: Set the href to our custom page once we have it ready 
                with cc1.container(height=container_height):
                    st.markdown(f'<p class="route-name"><a href="{url1}">{route_name1}</a></p>', unsafe_allow_html=True) 
                    st.markdown(f'<p class="route-details">Difficulty: {str(difficulty1)} - Rating: {str(average_rating1)}</p>', unsafe_allow_html=True) 
                    st.markdown(f"<p class='route-details'>{routeDetails1}</p>", unsafe_allow_html=True) 
                    st.markdown(f'<div class="trail-image-container"><a href="/trail-details?id={id1}&units={units}" target="_self"><img src={trailImage1} class="trail-image"></a></div>', unsafe_allow_html=True) 
                    st.markdown(summary1) 
               
                # column 2 trail details (check if we are in bounds)
                if (i+1) < trail_list_len: 
                    # TODO: Set the href to our custom page once we have it ready 
                    with cc2.container(height=container_height): 
                        st.markdown(f'<p class="route-name"><a href="{url2}">{route_name2}</a></p>', unsafe_allow_html=True) 
                        st.markdown(f'<p class="route-details">Difficulty: {str(difficulty2)} - Rating: {str(average_rating2)}</p>', unsafe_allow_html=True) 
                        st.markdown(f"<p class='route-details'>{routeDetails2}</p>", unsafe_allow_html=True) 
                        st.markdown(f'<div class="trail-image-container"><a href="/trail-details?id={id2}&units={units}" target="_self"><img src={trailImage2} class="trail-image"></a></div>', unsafe_allow_html=True) 
                        st.markdown(summary2) 

# -------------------------------------
# Label styling for queries and result
# -------------------------------------
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

# ------------------------------------------------------------------
# Set the stream output and trail list cache using session storage 
# ------------------------------------------------------------------
# NOTE: This was giving problems with duplicate widget IDs keep an eye 
#sessionStorage.deleteItem("stream_output_sesh", key="stream_output_sesh_1")
try:
    # Step 1: Store stream output in storage 
    if "stream_output" in st.session_state:
        if st.session_state["stream_output"] != "":
            sessionStorage.setItem("stream_output_sesh1",
                st.session_state["stream_output"], key="stream_output_sesh1") 
    
    # Step 2: Store trail list in storage 
    if "trail_list" in st.session_state:
        if len(st.session_state["trail_list"]) != 0:
            sessionStorage.setItem("trail_list_sesh1", 
                st.session_state["trail_list"], key="trail_list_sesh1") 
    
    # Step 3: Store query in storage 
    if "query" in st.session_state:
        if st.session_state["query"] != "":
            sessionStorage.setItem("query_sesh1",
                st.session_state["query"], key="query_sesh1") 
    
    # Step 4: Store location in storage 
    if "location" in st.session_state:
        if st.session_state["location"] != "":
            sessionStorage.setItem("location_sesh1",
                st.session_state["location"], key="location_sesh1") 
    
    # Step 5: Store in rag query storage 
    if "rag_query" in st.session_state:
        if st.session_state["rag_query"] != "":
            sessionStorage.setItem("rag_query_sesh1",
                st.session_state["rag_query"], key="rag_query_sesh1") 
    
    # Step 6: Store in easy storage 
    if "easy" in st.session_state:
        if st.session_state["easy"] != "":
            sessionStorage.setItem("easy_sesh1",
                st.session_state["easy"], key="easy_sesh1") 
    
    # Step 7: Store in intermediate storage 
    if "intermediate" in st.session_state:
        if st.session_state["intermediate"] != "":
            sessionStorage.setItem("intermediate_sesh1",
                st.session_state["intermediate"], key="intermediate_sesh1") 
    
    # Step 8: Store in difficult storage 
    if "difficult" in st.session_state:
        if st.session_state["difficult"] != "":
            sessionStorage.setItem("difficult_sesh1",
                st.session_state["difficult"], key="difficult_sesh1") 
    
    # Step 9: Store in units storage 
    if "units" in st.session_state:
        if st.session_state["units"] != "":
            sessionStorage.setItem("units_sesh1",
                st.session_state["units"], key="units_sesh1") 
except Exception as e:
    print(f"Cache exception: {e}")

