import requests
from bs4 import BeautifulSoup
from MTBTrailParser import MTBTrailParser 

# Read in the given trail url and parse the contents
# This will create the following trail db dictionaries:
# 	1. mtbTrailRoute MAP - high level trail route metadata
#	2. mtbTrailRouteDescriptions MAP - contains the mtb trail route descriptions 

class MTBTrailUrlParser:
	# this parses the trail url and creates tuple of dicts
	def parseTrail(self, url): 

		# URL parsing for MTB articles
		#URL = "https://www.mtbproject.com/trail/4939737/hangover-loop"
		page = requests.get(url)
		soup = BeautifulSoup(page.content, "html.parser")

		# initialize the mtb trail parser obj
		mtbTrailParser = MTBTrailParser(soup) 

		# create the trail map and print
		trailMap = mtbTrailParser.createTrailMap()
		# mtbTrailParser.printTrailMapContents(trailMap)

		# create the main MTB trail route 
		trailTitle = soup.find(id="trail-title")
		mtbTrailRoute = mtbTrailParser.createMTBTrailRoute(trailTitle) 
		mtbTrailRoute["trail_area"] = trailMap
		print("MTB Trail Route:")
		print(mtbTrailRoute)
		print("\n")

		# main text for trail descriptions 
		trailText = soup.find(id="trail-text")

		# create main section headers for trail text
		mainSectionHeaders = mtbTrailParser.createMainSectionHeaders(trailText)
		print(mainSectionHeaders)
		print("\n")

		# get the mtb body text from trail text element
		bodyText = mtbTrailParser.parseMainText(trailText)
		print(bodyText)
		print("\n")

		# create the mtb trail route descriptions
		trailTitle = trailTitle.text.strip()
		print("Trail title = " + trailTitle)

		# split the trail name so we can set the id
		trailTokens = trailTitle.split()
		trailId = trailTokens[0].lower()
		print("Trail id = " + trailId)

		mtbTrailRouteDescriptions = mtbTrailParser.createMTBTrailRouteDescriptions(
		trailId, mainSectionHeaders, bodyText)
		print("Number of descriptions = " + str(len(mtbTrailRouteDescriptions)))
		print(mtbTrailRouteDescriptions)
		print("\n")
  
		return (mtbTrailRoute, mtbTrailRouteDescriptions)