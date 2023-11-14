"""Area class for storing trails location
areaRef - link to the area
areaName - area name (state, county, etc.)

    Returns:
            _type_: area obj
    """


class Area:
    def __init__(self, areaRef, areaName):
        self.areaRef = areaRef
        self.areaName = areaName

    def show_contents(self):
        print(f"Area = {self.areaRef} : {self.areaName}")

        """_summary_

Trail Area class containing all area info for the trail system
            Returns:
                    _type_: _description_
            """

# TODO: This needs to be updated to output object to dict/json format to 
# store in the MongoDB
class TrailArea:
    def __init__(self):
        self.trailKeys = {
            1: "state",
            2: "county",
            3: "trail_system"
        }
        self.trailMap = {}

    def show_contents(self):
        print(f"Area: {self.areaRef} - {self.areaName}")

    def parse_area_list(self, areaList):
        # create the area obj
        for i in range(1, len(areaList)):
            key = self.trailKeys[i]
            areaJson = areaList[i]
            areaObj = Area(areaJson["item"], areaJson["name"])
            self.trailMap[key] = areaObj

        return self.trailMap