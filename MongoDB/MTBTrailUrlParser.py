import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import cssutils
from MTBTrailParser import MTBTrailParser

# Read in the given trail url and parse the contents
# This will create the following trail db dictionaries:
# 	1. mtbTrailRoute MAP - high level trail route metadata
# 2. mtbTrailRouteDescriptions MAP - contains the mtb trail route descriptions
import re

# TODO: Increase total retries, factor and forcelist (429)
# TODO: backoff of 2, total retries = 8
class MTBTrailUrlParser:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=8, backoff_factor=2, status_forcelist=[429,500,502,503,504])
        self.session.mount('https://www.mtbproject.com', HTTPAdapter(max_retries=retries))

    # parse the image from photo link
    def parseImage(self, imgUrl):
        img_page = self.session.get(imgUrl)
        soup = BeautifulSoup(img_page.content, "html.parser")
        mainPhoto = soup.find("img", class_="main-photo") 
        if mainPhoto: 
            imgUrl = mainPhoto["src"].strip() 
            imgUrl = imgUrl.split("?")[0] 
            return imgUrl
        else:
            return None

    # this parses the trail url and creates tuple of dicts
    def parseTrail(self, trail_url):
        
        # URL parsing for MTB articles
        page = self.session.get(trail_url) 
        soup = BeautifulSoup(page.content, "html.parser")

        # initialize the mtb trail parser obj
        mtbTrailParser = MTBTrailParser(soup)

        # get the images from the carousel
        # class = carousel-inner
        # class = carousel-item
        imageItems = soup.find_all("div", class_="carousel-item")
        imageUrls = [] 
        for i in imageItems:

            # check attrs for style and img src
            attrs = i.attrs
            if "style" in attrs:
                style = attrs["style"]
                style = cssutils.parseStyle(style)
                img_url = style["background-image"]
                img_url = img_url.replace('url(', '').replace(')', '')
                img_url = img_url.split("?")[0] 
                imageUrls.append(img_url) 
            elif "data-src" in attrs:
                img_url = attrs["data-src"]
                img_url = img_url.split("?")[0] 
                imageUrls.append(img_url)
            else:
                # if no attrs exist need to get the url
                # from the main image item
                photoElem = i.find('a', class_="photo-link")
                if photoElem: 
                    photoLink = photoElem['href']
                    img_url = self.parseImage(photoLink)
                    if img_url: 
                        imageUrls.append(img_url)

        #print(f"Trail url = {trail_url}")
        #print(f"Image urls (len = {len(imageUrls)})")
        #print(imageUrls)
        #print("\n")

        # create the trail map and print
        trailMap = mtbTrailParser.createTrailMap(trail_url)
        if trailMap is None:
            return None 

        # get the trail stats such as elevation change/distance
        trailStats = soup.find(id="trail-stats-bar")
        if trailStats is None:
            return None
        trailStatsMap = mtbTrailParser.createTrailStatsMap(trailStats)

        # get the toolbox for the gpx file and driving directions
        toolBox = soup.find(id="toolbox")
        if toolBox is None:
            return None

        # create the main MTB trail route
        trailTitle = soup.find(id="trail-title")
        if trailTitle is None:
            return None
        mtbTrailRoute = mtbTrailParser.createMTBTrailRoute(trailTitle, toolBox, trail_url)
        if mtbTrailRoute is None:
            return None
        
        trailId = mtbTrailRoute["_id"] 
        mtbTrailRoute["trail_area"] = trailMap
        mtbTrailRoute["trail_stats"] = trailStatsMap 
        mtbTrailRoute["trail_images"] = imageUrls

        # main text for trail descriptions
        trailText = soup.find(id="trail-text")
        if trailText is None:
            return None

        # create main section headers for trail text
        mainSectionHeaders = mtbTrailParser.createMainSectionHeaders(trailText)

        # get the mtb body text from trail text element
        bodyText = mtbTrailParser.parseMainText(trailText)
        mtbTrailRouteDescriptions = mtbTrailParser.createMTBTrailRouteDescriptions(trailId, mainSectionHeaders, bodyText)
      
        print(f"{trail_url},", end="", flush=True) 
        return (mtbTrailRoute, mtbTrailRouteDescriptions)
