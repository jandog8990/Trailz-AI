"""Area class for storing trails location
areaName - area name (state, county, etc.)
areaRef - link to the area

    Returns:
            _type_: area obj
    """


class Area:
    def __init__(self, areaName, areaRef):
        self.areaName = areaName
        self.areaRef = areaRef

    def show_contents(self):
        print(f"Area = {self.areaName} : {self.areaRef}")

        """_summary_

Trail Area class containing all area info for the trail system
            Returns:
                    _type_: _description_
            """

# TODO: We need to know that there will be sub-areas that exist between
# the state and trail system, these sub areas can be of any length 
class TrailArea:
    def __init__(self):
        self.STATE_KEY = "state" 
        self.SUB_AREA_KEY = "sub_area"
        self.TRAIL_SYSTEM_KEY = "trail_system"
 
        self.trailKeys = {
            1: "state",
            2: "sub_area", 
            3: "trail_system"
        }
        self.extendedTrailKeys = {
            1: "state",
            2: "county",
            3: "city",
            4: "trail_system"
        }
        self.trailMap = {}

    def show_contents(self):
        print(f"Area: {self.areaName} - {self.areaRef}")

    def parse_area_list(self, areaList, url):
        # create the area obj
        # this entire logic will be replaced with
        # the trail list keys directly 

        # TODO: Let's make each value in the map an array of Area objects, the
        # first will be the state object and the last will be trail system obj 
        areaList.pop(0) 
        stateJson = areaList.pop(0)
        
        # state should always be present
        stateArea = Area(stateJson["name"], stateJson["item"]) 
        self.trailMap[self.STATE_KEY] = [stateArea]
       
        # the area list 
        if len(areaList) == 0:
            print("Area list has zero elements:")
            print(f"Area list url = {url}") 
            print(f"State json = {stateJson}")
            print(f"Area list len = {len(areaList)}") 
            print(f"=> Return trailMap")  
            print("\n")
        else: 
            trailJson = areaList.pop(-1)
            trailArea = Area(trailJson["name"], trailJson["item"])
          
            # let's start creating the trail map of Area object arrays
            self.trailMap[self.TRAIL_SYSTEM_KEY] = [trailArea] 
          
            # let's loop through the rest of the area list and create the sub area
            subAreaList = [] 
            for areaJson in areaList:
                subArea = Area(areaJson["name"], areaJson["item"])
                subAreaList.append(subArea)
            self.trailMap[self.SUB_AREA_KEY] = subAreaList 
        
        return self.trailMap
