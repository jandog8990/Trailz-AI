import streamlit as st
import streamlit.components.v1 as components
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
#storageContents = sessionStorage.getAll()

# create the description list from text
def parse_text(text):
    return list(filter(None, text.rstrip().split("\n")))

def load_trail_detail(trail_id):
    return ragUtility.query_mongodb_trail_detail(trail_id)

storageContents = sessionStorage.getAll() 
trailDetail = {}
if len(storageContents) > 0:
    if "trail_id_sesh2" not in storageContents:
        trailDetail = load_trail_detail(trail_id)  
    else:
        if trail_id != storageContents["trail_id_sesh2"]:
            trailDetail = load_trail_detail(trail_id)  
        else:            
            trailDetail = storageContents["trail_detail_sesh2"] if "trail_detail_sesh2" in storageContents else {}

if trailDetail and len(trailDetail) > 0:

    # get the trail fields from the details
    routeName = trailDetail["route_name"]
    difficulty = trailDetail["trail_rating"]
    average_rating = trailDetail["average_rating"]
    descMap = trailDetail["descMap"]
    trailImages = trailDetail["trail_images"]
    trailStats = trailDetail["trail_stats"]
    gpxFile = trailDetail["gpx_file"] 
    routeDetails = trailUtility.createTrailStats(trailStats, units)
    print(f"GPX file = {gpxFile}")

    imageElements = "" 
    dotElements = "" 
    count = 0 
    for img in trailImages:
        count += 1 
        imageElements += f"""
        <div class="mySlides fade">
          <div class="numbertext">{count} / {len(trailImages)}</div>
          <img src={img} class="trail-image">
        </div>
        """
        dotElements += f""" 
          <span class="dot" onclick="currentSlide({count})"></span>
        """

    # top container with trail name and info 
    with st.container():
        st.title(routeName) 
        st.markdown(f'<p class="route-details">Difficulty: {str(difficulty)} - Rating: {str(average_rating)}</p>', unsafe_allow_html=True) 
        st.markdown(f"<p class='route-details'>{routeDetails}</p>", unsafe_allow_html=True) 
        st.markdown("<br>", unsafe_allow_html=True)
   
    # image carousel container
    with st.container():

        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        * {box-sizing: border-box}
        body {font-family: Verdana, sans-serif; margin:0}
        .mySlides {display: none}
        img {vertical-align: middle;}

        /* Slideshow container */
        .slideshow-container {
          max-width: 1000px;
          position: relative;
            margin: auto; 
        }

        .trail-image {
            width: 100%;
            height: 350px; 
            object-fit: cover;
            display: block;
            margin-left: auto; 
            margin-right: auto; 
        }

        /* Next & previous buttons */
        .prev, .next {
          cursor: pointer;
          position: absolute;
          top: 50%;
          width: auto;
          padding: 16px;
          margin-top: -22px;
          color: white;
          font-weight: bold;
          font-size: 18px;
          transition: 0.6s ease;
          border-radius: 0 3px 3px 0;
          user-select: none;
        }

        /* Position the "next button" to the right */
        .next {
          right: 0;
          border-radius: 3px 0 0 3px;
        }

        /* On hover, add a black background color with a little bit see-through */
        .prev:hover, .next:hover {
          background-color: rgba(0,0,0,0.8);
        }

        /* Number text (1/3 etc) */
        .numbertext {
          color: #f2f2f2;
          font-size: 12px;
          padding: 8px 12px;
          position: absolute;
          top: 0;
        }

        /* The dots/bullets/indicators */
        .dot {
          cursor: pointer;
          height: 15px;
          width: 15px;
          margin: 0 2px;
          background-color: #bbb;
          border-radius: 50%;
          display: inline-block;
          transition: background-color 0.6s ease;
        }

        .active, .dot:hover {
          background-color: #717171;
        }

        /* Fading animation */
        .fade {
          animation-name: fade;
          animation-duration: 1.5s;
        }

        @keyframes fade {
          from {opacity: .4}
          to {opacity: 1}
        }

        /* On smaller screens, decrease text size */
        @media only screen and (max-width: 300px) {
          .prev, .next,.text {font-size: 11px}
        }
        </style>
        </head>
        <body>
        """ +
        f"""
        <div class="slideshow-container">
            {imageElements}
            <a class="prev" onclick="plusSlides(-1)">❮</a>
            <a class="next" onclick="plusSlides(1)">❯</a>
        </div>
        <br>

        <div style="text-align:center">
            {dotElements}
        </div>
        """ +
        """
        <script>
        let slideIndex = 1;
        showSlides(slideIndex);

        function plusSlides(n) {
          showSlides(slideIndex += n);
        }

        function currentSlide(n) {
          showSlides(slideIndex = n);
        }

        function showSlides(n) {
          let i;
          let slides = document.getElementsByClassName("mySlides");
          let dots = document.getElementsByClassName("dot");
          if (n > slides.length) {slideIndex = 1}
          if (n < 1) {slideIndex = slides.length}
          for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
          }
          for (i = 0; i < dots.length; i++) {
            dots[i].className = dots[i].className.replace(" active", "");
          }
          slides[slideIndex-1].style.display = "block";
          dots[slideIndex-1].className += " active";
        }
        </script>

        </body>
        </html>
        """, height=390)
   
    # trail map container using mapbox
    with st.container():


    # lower container trail details 
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
        </style>""", unsafe_allow_html=True) 
        
    try:
        sessionStorage.setItem("trail_id_sesh2", trail_id, key="trail_id_sesh2")
        sessionStorage.setItem("trail_detail_sesh2", trailDetail, key="trail_detail_sesh2")
    except Exception as e:
        print(f"Cache exception: {e}")
