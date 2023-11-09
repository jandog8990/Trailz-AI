import requests
from bs4 import BeautifulSoup
import re
import json

from Area import TrailArea

# URL parsing for MTB articles
URL = "https://www.mtbproject.com/trail/4939737/hangover-loop"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

# titlebar
titlebar = soup.find(id="title-bar")

print("---- TITLE BAR ----")
print(titlebar.prettify())
print("\n")

# TODO: Within the title bar lies the areas - areas needed for DB
# storage to recommend trailz based on location of user
# within the script tags lives the item list for area bread
script_obj = titlebar.find('script')
json_obj = json.loads(script_obj.text)
print("---- SCRIPT OBJ ----")
print(json_obj)
print("\n")

# lets get each of the area items and store them as
# 1. State
# 2. County 
# 3. TrailSystem
areaList = json_obj['itemListElement']
stateObj = areaList[1]
countyObj = areaList[2]
trailSystemObj = areaList[3]
trailArea = TrailArea()
trailMap = trailArea.parse_area_list(areaList)
trailArea.trail_map_contents()


# header
trailTitle = soup.find(id="trail-title")
trailTitle = trailTitle.text.strip()
print("Trail title = " + trailTitle)

# split the trail name so we can set the id
trailTokens = trailTitle.split()
trail_id = trailTokens[0].lower()
print("Trail id = " + trail_id)

# difficulty
diffbanner = soup.find("div", class_="title")
difficulty = soup.find("span", class_="difficulty-text")
difficulty = difficulty.text.strip()
print("Difficulty = " + difficulty)

# trail subheader containing reviews
metaWrapper = soup.find("div", class_="stars-container")
topRatings = metaWrapper.find("span", class_="small")
totalRatings = topRatings.text.strip()

# separate trail ratings and num ratings
ratingTokens = totalRatings.split()
numRatings = ratingTokens[1].replace('(', '')
numRatings = numRatings.replace(')', '')
avgRating = ratingTokens[0]
print("Number of ratings = " + numRatings)
print("Average rating = " + avgRating)
print("\n")

# Let's now create the main table for the trailz route
mtb_trail_route = {
    "_id": trail_id,
    "route_name": trailTitle,
    "difficulty": difficulty,
    "average_rating": avgRating,
    "num_ratings": numRatings
}
print("MTB trail route = ")
print(mtb_trail_route)