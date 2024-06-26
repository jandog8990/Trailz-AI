# init db utility objects
import streamlit as st
import os
import re
from RAGUtility import RAGUtility
from TrailUtility import TrailUtility
from streamlit_session_browser_storage import SessionStorage

# get environment and query params
defaultImg = os.environ["TRAILZ_AI_IMG"]
trail_id = st.query_params.id
units = st.query_params.units

# TODO: Cache the id and units and compare to the incoming params
# if the incoming id/units does not match then query the DB
# else access the cache for values

# query MongoDB for the trail details
ragUtility = RAGUtility() 
trailUtility = TrailUtility()
sessionStorage = SessionStorage()
#sessionStorage.deleteAll()
storageContents = sessionStorage.getAll()

# create the description list from text
def parse_text(text):
    return list(filter(None, text.rstrip().split("\n")))

def load_trail_detail(trail_id):
    print("Query mongoDB!") 
    print("\n") 
    return ragUtility.query_mongodb_trail_detail(trail_id)

storageContents = sessionStorage.getAll() 
trailDetail = {}
if len(storageContents) > 0:
    if "trail_id_sesh2" not in storageContents:
        print("Trial id not in Storage!") 
        trailDetail = load_trail_detail(trail_id)  
    else:
        if trail_id != storageContents["trail_id_sesh2"]:
            print("Trail id != storage id")
            print(f"trail id = {trail_id}")
            print(f"storage id = {storageContents['trail_id_sesh2']}")
            trailDetail = load_trail_detail(trail_id)  
        else:            
            print("Trail id load from cache!") 
            print("trail id == storage id") 
            print("\n")
            trailDetail = storageContents["trail_detail_sesh2"] if "trail_detail_sesh2" in storageContents else {}

if trailDetail and len(trailDetail) > 0:
    print("Trail detail exists! => load page!")

    # DESC MAP needs to be reimplemented since we delete it

    # get the trail fields from the details
    routeName = trailDetail["route_name"]
    difficulty = trailDetail["trail_rating"]
    average_rating = trailDetail["average_rating"]
    descMap = trailDetail["descMap"]
    trailImages = trailDetail["trail_images"]
    trailStats = trailDetail["trail_stats"]
    routeDetails = trailUtility.createTrailStats(trailStats, units)

    # top container with trail name and images
    with st.container():
        st.title(routeName) 
        st.markdown(f'<p class="route-details">Difficulty: {str(difficulty)} - Rating: {str(average_rating)}</p>', unsafe_allow_html=True) 
        st.markdown(f"<p class='route-details'>{routeDetails}</p>", unsafe_allow_html=True) 
        st.markdown("<br>", unsafe_allow_html=True)

    # lower container trail description
    with st.container():
        st.header("Trail Details", divider='rainbow') 
        if "Preface" in descMap: 
            descList = parse_text(descMap["Preface"]) 
            st.markdown(f"### Preface") 
            for desc in descList: 
                st.markdown(f'<p class="description">{desc}</p>', unsafe_allow_html=True)
        if "Overview" in descMap: 
            descList = parse_text(descMap["Overview"]) 
            st.markdown(f"### Overview") 
            for desc in descList: 
                st.markdown(f'<p class="description">{desc}</p>', unsafe_allow_html=True)
        
        for key, val in descMap.items():
            if key != "Preface" and key != "Overview": 
                descList = parse_text(val) 
                st.markdown(f"### {key}") 
                for desc in descList: 
                    st.markdown(f'<p class="description">{desc}</p>', unsafe_allow_html=True)

    # style for the containers and contents
    st.markdown("""
        <style> 
        .route-details {
            font-size: 21px; 
            margin-bottom: 0px; 
            margin-top: 0px; 
        }
        .description {
            font-size: 18px; 
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
        </style>""", unsafe_allow_html=True) 

    try:
        sessionStorage.setItem("trail_id_sesh2", trail_id, key="trail_id_sesh2")
        sessionStorage.setItem("trail_detail_sesh2", trailDetail, key="trail_detail_sesh2")
    except Exception as e:
        print(f"Cache exception: {e}")
