import requests
from bs4 import BeautifulSoup
import re
import json

from Area import TrailArea

# URL parsing for MTB articles
URL = "https://www.mtbproject.com/trail/4939737/hangover-loop"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

# TODO: Think of how to separate this into classes so when we bring 
# in multiple trails we can parse them accordingly

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

def createTrailMetadata(trailTitle):
    # header
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

def createMainSectionHeaders(trailText):
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

# create a function that takes in main text and parses
def parseMainText(trailText):
    # Main section text starts at index = 2
    mainText = trailText.find_all("div", class_="mb-1")
    start = 2
    end = len(mainText)
    count = 0
    mainBody = []
    for idx in range(start, end-1):
        elem = mainText[idx]
        strippedText = elem.text.strip()
        newText = re.sub(' +', ' ', strippedText)
        newText = re.sub('\n', '\n', newText)
        mainBody.append(newText)
        count+=1
    
    return mainBody

# create the trail route descriptions from body text and headers
def createTrailRouteDescriptions(trailId, mainSectionHeaders, bodyText):
    # Let's create the dictionary of section headers to main text
    mainTextMap = {}
    start = 0
    end = len(mainSectionHeaders)-1
    for i in range(start, end):
        header = mainSectionHeaders[i]
        text = bodyText[i]
        mainTextMap[header] = text

    mtb_trail_route_descriptions = []
    print("Main map size = " + str(len(mainTextMap)))
    for key in mainTextMap:
        description = mainTextMap[key]
        print("Key = {0}".format(key))
        print("Value = {0}".format(mainTextMap[key]))
        print("\n")
        
        descObj = {
            "_id": key.lower(),
            "key": key,
            "text": description,
            "mtb_trail_route_id": trailId 
        }
        mtb_trail_route_descriptions.append(descObj)  
    return mtb_trail_route_descriptions

# create the trail map and print
trailMap = createTrailMap()
trailMapContents(trailMap)

# create the trail metadata
trailTitle = soup.find(id="trail-title")
trailMetadata = createTrailMetadata(trailTitle) 
trailMetadata["trail_area"] = trailMap
print("Trail metadata:")
print(trailMetadata)
print("\n")

# main text for trail descriptions 
trailText = soup.find(id="trail-text")

# create main section headers for trail text
mainSectionHeaders = createMainSectionHeaders(trailText)
print(mainSectionHeaders)
print("\n")

# get the mtb body text from trail text element
bodyText = parseMainText(trailText)
print(bodyText)
print("\n")

# create the mtb trail route descriptions
trailTitle = trailTitle.text.strip()
print("Trail title = " + trailTitle)

# split the trail name so we can set the id
trailTokens = trailTitle.split()
trailId = trailTokens[0].lower()
print("Trail id = " + trailId)

mtbTrailRouteDescriptions = createTrailRouteDescriptions(trailId, mainSectionHeaders, bodyText)
print("Number of descriptions = " + str(len(mtbTrailRouteDescriptions)))
print(mtbTrailRouteDescriptions)

# next connect to the database