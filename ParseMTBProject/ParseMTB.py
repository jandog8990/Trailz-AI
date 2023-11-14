import requests
from bs4 import BeautifulSoup
import re
import json

from Area import TrailArea

# URL parsing for MTB articles
URL = "https://www.mtbproject.com/trail/4939737/hangover-loop"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

def createTrailMap():
    # titlebar
    titlebar = soup.find(id="title-bar")

    # TODO: Within the title bar lies the areas - areas needed for DB
    # storage to recommend trailz based on location of user
    # within the script tags lives the item list for area bread
    script_obj = titlebar.find('script')
    json_obj = json.loads(script_obj.text)

    # lets get each of the area items and store them as
    # 1. State
    # 2. County 
    # 3. TrailSystem
    areaList = json_obj['itemListElement']
    trailArea = TrailArea()
    return trailArea.parse_area_list(areaList)

def trailMapContents(trailMap):
    for key, val in trailMap.items():
        print(f"Key = {key}")
        print("val:")
        val.show_contents()
        print("\n")

def createTrailMetadata():
    # header
    trailTitle = soup.find(id="trail-title")
    trailTitle = trailTitle.text.strip()

    # split the trail name so we can set the id
    trailTokens = trailTitle.split()
    trail_id = trailTokens[0].lower()

    # difficulty
    diffbanner = soup.find("div", class_="title")
    difficulty = soup.find("span", class_="difficulty-text")
    difficulty = difficulty.text.strip()

    # trail subheader containing reviews
    metaWrapper = soup.find("div", class_="stars-container")
    topRatings = metaWrapper.find("span", class_="small")
    totalRatings = topRatings.text.strip()

    # separate trail ratings and num ratings
    ratingTokens = totalRatings.split()
    numRatings = ratingTokens[1].replace('(', '')
    numRatings = numRatings.replace(')', '')
    avgRating = ratingTokens[0]

    # Let's now create the main table for the trailz route
    return {
        "_id": trail_id,
        "route_name": trailTitle,
        "difficulty": difficulty,
        "average_rating": avgRating,
        "num_ratings": numRatings
    }

def createMainSectionHeaders():
    # main content area
    trailText = soup.find(id="trail-text")

    #get the FEATURES
    features = trailText.find_all("h3", class_="mr-2")

    # let's try and find the main text header sections
    h3Tags = trailText.find_all("h3")
    h3Count = 0
    mainSectionHeaders = []
    for tag in h3Tags:
        h3Class = tag.get('class')
        h3Text = tag.text.strip()
        h3Count += 1
        if h3Class == None:
            sectionHeader = re.sub(' +', ' ', h3Text)
            mainSectionHeaders.append(sectionHeader)

    return mainSectionHeaders

# create the trail map and print
trailMap = createTrailMap()
trailMapContents(trailMap)

# create the trail metadata
trailMetadata = createTrailMetadata() 
trailMetadata["trail_area"] = trailMap
print("Trail metadata:")
print(trailMetadata)
print("\n")

# create main section headers for trail text
mainSectionHeaders = createMainSectionHeaders()
print(mainSectionHeaders)