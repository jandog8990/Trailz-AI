import re
import json
from Area import TrailArea

# -------------------------------------------------------
# ------- Parsing Methods for MTB Trail Page Data -------
# -------------------------------------------------------

class MTBTrailParser:
    def __init__(self, soup):
        self.soup = soup
         
    def createTrailMap(self, url):
        # titlebar can be none so make sure and check
        titlebar = self.soup.find(id="title-bar")

        # titlebar can be None -> go to next
        if titlebar is None:
            return None
        
        # TODO: Within the title bar lies the areas - areas needed for DB
        # storage to recommend trailz based on location of user
        # within the script tags lives the item list for area bread
        script_obj = titlebar.find('script')
        if script_obj is None:
            return None
        json_obj = json.loads(script_obj.text)

        # lets get each of the area items and store them as
        # 1. State
        # 2. County 
        # 3. TrailSystem
        areaList = json_obj['itemListElement']
        trailArea = TrailArea()
       
        # first check that the area list is greater than 0
        if len(areaList) == 0:
            print(f"Area list EMPTY for url = {url}")
            return None 
        return trailArea.parse_area_list(areaList, url)

    def printTrailMapContents(self, trailMap):
        print("Trail Map Contents:") 
        for key, val in trailMap.items():
            print(f"Key = {key}")
            print("val:")
            val.show_contents()
            print("\n")

    def parseElevation(self, block):
        impBlock = block.find_all("span", class_="imperial")
        metBlock = block.find_all("span", class_="metric")
        impHighElev = impBlock[0].text.strip() 
        impLowElev = impBlock[1].text.strip() 
        metHighElev = metBlock[0].text.strip() 
        metLowElev = metBlock[1].text.strip() 
        impHighLow = (impHighElev, impLowElev)
        metHighLow = (metHighElev, metLowElev)
        return {"impElev": impHighLow, "metElev": metHighLow}

    # create the trail stats (elev, mi, etc)
    # NOTE:
    # B0 = Dist and % singletrack
    # B1 = Max elev/min elev
    # B3 = Climbing elev/desc elev
    # B4 = Avg/max grade (steepness)
    def createTrailStats(self, trailStats):
        statBlocks = trailStats.find_all('div', class_="stat-block")
        distBlock = statBlocks[0]
        overallElevBlock = statBlocks[1]
        bikingElevBlock = statBlocks[2]
        gradeBlock = statBlocks[3]
       
        # parse the distances block
        miBlock = distBlock.find("span", class_="imperial")
        kmBlock = distBlock.find("span", class_="metric")
        singleTrack = distBlock.find_all("h3", class_='')[2].text
        impDist = miBlock.find("h3").text
        impUnits = miBlock.find("span", class_="units").text 
        metDist = kmBlock.find("h3").text
        metUnits = kmBlock.find("span", class_="units").text 
        
        impString = impDist + " " + impUnits
        metString = metDist + " " + metUnits
        singleTrackString = singleTrack + " Singletrack"
        print(f"Impt dist = {impString}") 
        print(f"Metric dist = {metString}") 
        print(f"Single track = {singleTrackString}")
        print("\n")
      
        # parse overall elev block
        elevMap = self.parseElevation(overallElevBlock) 
        impElev = elevMap["impElev"] 
        metElev = elevMap["metElev"] 
        impHigh = impElev[0]
        impLow = impElev[1]
        metHigh = metElev[0]
        metLow = metElev[1]

        print(f"Imp elev = {impHigh} {impLow}")
        print(f"Met elev = {metHigh} {metLow}")
        print("\n")

        # parse elev change block
        elevChangeMap = self.parseElevation(bikingElevBlock) 
        impElevChange = elevChangeMap["impElev"] 
        metElevChange = elevChangeMap["metElev"] 
        impElevHigh = impElevChange[0]
        impElevLow = impElevChange[1]
        metElevHigh = metElevChange[0]
        metElevLow = metElevChange[1]
        print(f"Imp elev change = {impElevHigh} {impElevLow}")
        print(f"Met elev change = {metElevHigh} {metElevLow}")
        print("\n")
       
        # parse the grade
        grades = gradeBlock.find_all("h3")
        print("Grades:")
        print(grades)
        gradeArr = gradeBlock.text.split("</br>")[0].splitlines()
        gradeArr = [x.strip() for x in gradeArr if x.strip()] 
        avgGrade = gradeArr[0] + ' ' + gradeArr[1]
        maxGrade = gradeArr[2] + ' ' + gradeArr[3]
        print(f"avgGrade = {avgGrade}")
        print(f"maxGrade = {maxGrade}")
        print("\n")

        # let's now make a map for the stats
        statMap = {}

    # create trail rating using the difficulty string
    def createTrailRating(self, difficulty):
        ratingMap = {
            "Easy": "Green",
            "Easy/Intermediate": "Green/Blue",
            "Intermediate": "Blue",
            "Intermediate/Difficult": "Blue/Black",
            "Difficult": "Black",
            "Very Difficult": "Double Black"
        }
        
        if difficulty in ratingMap:
            return ratingMap[difficulty]
        else:
            return "Unknown"

    # create the main mtb trail route data
    def createMTBTrailRoute(self, trailTitle, toolBox, url):
        # trail title from the main header 
        trailTitle = trailTitle.text.strip()
       
        # toolbox from the main page
        pattern1 = re.compile(r'Driving directions')
        pattern2 = re.compile(r'Download GPX File')
        elem1 = toolBox.find('a', href=True, text=pattern1)
        elem2 = toolBox.find('a', href=True, text=pattern2)
        driving_directions = elem1['href']
        gpx_file = elem2['href']

        # split the trail name so we can set the id
        trailTokens = trailTitle.split()
        #trail_id = trailTokens[0].lower()
        trail_id = trailTitle.lower()

        # difficulty
        diffbanner = self.soup.find("div", class_="title")
        difficulty = self.soup.find("span", class_="difficulty-text")
        if (difficulty is None) or (difficulty == ""):
            return None
        difficulty = difficulty.text.strip()

        # trail rating (colors)
        trail_rating = self.createTrailRating(difficulty) 

        # trail subheader containing reviews
        metaWrapper = self.soup.find("div", class_="stars-container")
        if metaWrapper is None:
            return None
        topRatings = metaWrapper.find("span", class_="small")
        
        # strip the top ratings if they exist
        if topRatings is None:
            return None 
        totalRatings = topRatings.text.strip()

        # separate trail ratings and num ratings
        ratingTokens = totalRatings.split()
        numRatings = ratingTokens[1].replace('(', '')
        numRatings = numRatings.replace(')', '')
        avgRating = ratingTokens[0]

        # Let's now create the main table for the trailz route
        return {
            "_id": trail_id,
            "trail_url": url, 
            "driving_directions": driving_directions,
            "gpx_file": gpx_file,
            "route_name": trailTitle,
            "difficulty": difficulty,
            "trail_rating": trail_rating,
            "average_rating": float(avgRating),
            "num_ratings": int(numRatings)
        }

    def createMainSectionHeaders(self, trailText):
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
    def parseMainText(self, trailText):
        # Main section text starts at index = 2
        mainText = trailText.find_all("div", class_="mb-1")
        start = 2
        end = len(mainText)
        count = 0
        mainBody = []
         
        for idx in range(start, end):
            elem = mainText[idx]
            # strippedText = elem.text 
            strippedText = elem.text.strip()
            newText = re.sub(' +', ' ', strippedText)
            newText = re.sub('\n', '\n', newText)
            mainBody.append(newText)
            count+=1
        
        return mainBody

    # create the mtb trail route descriptions from body text and headers
    def createMTBTrailRouteDescriptions(self, trailId, mainSectionHeaders, bodyText):
        # Let's create the dictionary of section headers to main text
       
        # need to remove sub section headers that do not match to descriptions 
        race = "race"
        contacts = "contacts"
        mainSectionHeaders = [header for header in mainSectionHeaders 
            if (race not in header.lower()) and (contacts not in header.lower())]
        headersLen = len(mainSectionHeaders)
         
        start = 0
        end = headersLen

        mainTextMap = {}
        for i in range(start, end):
            try: 
                header = mainSectionHeaders[i]
                text = bodyText[i]
                mainTextMap[header] = text
            except IndexError as e:
                print(f"--- Index exception = {e} ---")
                print(f"Trail ID = {trailId}") 
                print(f"Index = {i}")
                print(f"Header = {header}") 
                print(f"Main section headers len = {headersLen}") 
                print(f"Body text length = {len(bodyText)}") 
                print("Main section headers:")
                print(mainSectionHeaders) 
                print("\n")
 
        mtb_trail_route_descriptions = []
        for key in mainTextMap:
            description = mainTextMap[key]
           
            # trail id and the key from the text type gives the PK 
            # the FK used in this table is what relates it to the route 
            primaryKey = trailId + " " + key.lower() 
            descObj = {
                "_id": primaryKey, 
                "key": key,
                "text": description,
                "mtb_trail_route_id": trailId 
            }
           
            mtb_trail_route_descriptions.append(descObj)  
        return mtb_trail_route_descriptions
