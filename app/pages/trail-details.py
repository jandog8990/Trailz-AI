# init db utility objects
import streamlit as st
from RAGUtility import RAGUtility
from TrailUtility import TrailUtility
import os
import re

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
trailDetail = ragUtility.query_mongodb_trail_detail(trail_id)

# get the trail fields from the details
routeName = trailDetail["route_name"]
difficulty = trailDetail["trail_rating"]
average_rating = trailDetail["average_rating"]
descMap = trailDetail["descMap"]
trailImages = trailDetail["trail_images"]
trailStats = trailDetail["trail_stats"]
routeDetails = trailUtility.createTrailStats(trailStats, units)

# create the description list from text
def parse_text(text):
    return list(filter(None, text.rstrip().split("\n")))

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

# top container with trail name and images
with st.container():
    st.title(routeName) 
    #st.markdown(f"""# {routeName}\n<hr style="height:8px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True) 
    #st.markdown(f"# {routeName}")
    #st.divider() 
    st.markdown(f'<p class="route-details">Difficulty: {str(difficulty)} - Rating: {str(average_rating)}</p>', unsafe_allow_html=True) 
    st.markdown(f"<p class='route-details'>{routeDetails}</p>", unsafe_allow_html=True) 
    st.markdown("<br>", unsafe_allow_html=True)

# lower container trail description
with st.container():
    st.header("Trail Details", divider='rainbow') 
    if "Preface" in descMap: 
        descList = parse_text(descMap["Preface"]) 
        del descMap["Preface"] 
        st.markdown(f"### Preface") 
        for desc in descList: 
            st.markdown(f'<p class="description">{desc}</p>', unsafe_allow_html=True)
    if "Overview" in descMap: 
        descList = parse_text(descMap["Overview"]) 
        del descMap["Overview"] 
        st.markdown(f"### Overview") 
        for desc in descList: 
            st.markdown(f'<p class="description">{desc}</p>', unsafe_allow_html=True)
    
    for key, val in descMap.items():
        descList = parse_text(val) 
        st.markdown(f"### {key}") 
        for desc in descList: 
            st.markdown(f'<p class="description">{desc}</p>', unsafe_allow_html=True)
