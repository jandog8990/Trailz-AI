import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from MTBTrailParser import MTBTrailParser

# Read in the given trail url and parse the contents
# This will create the following trail db dictionaries:
# 	1. mtbTrailRoute MAP - high level trail route metadata
# 2. mtbTrailRouteDescriptions MAP - contains the mtb trail route descriptions
import re

class MTBTrailUrlParser:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500,502,503,504])
        self.session.mount('https://www.mtbproject.com', HTTPAdapter(max_retries=retries))
    
    # this parses the trail url and creates tuple of dicts
    def parseTrail(self, url):

        # URL parsing for MTB articles
        page = self.session.get(url) 
        soup = BeautifulSoup(page.content, "html.parser")

        # initialize the mtb trail parser obj
        mtbTrailParser = MTBTrailParser(soup)

        # create the trail map and print
        trailMap = mtbTrailParser.createTrailMap(url)
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
        mtbTrailRoute = mtbTrailParser.createMTBTrailRoute(trailTitle, toolBox, url)
        if mtbTrailRoute is None:
            return None
        trailId = mtbTrailRoute["_id"] 

        mtbTrailRoute["trail_area"] = trailMap
        mtbTrailRoute["trail_stats"] = trailStatsMap 

        # main text for trail descriptions
        trailText = soup.find(id="trail-text")
        if trailText is None:
            return None

        # create main section headers for trail text
        mainSectionHeaders = mtbTrailParser.createMainSectionHeaders(trailText)

        # get the mtb body text from trail text element
        bodyText = mtbTrailParser.parseMainText(trailText)
        mtbTrailRouteDescriptions = mtbTrailParser.createMTBTrailRouteDescriptions(trailId, mainSectionHeaders, bodyText)
       
        print(".", end="", flush=True) 
        return (mtbTrailRoute, mtbTrailRouteDescriptions)
