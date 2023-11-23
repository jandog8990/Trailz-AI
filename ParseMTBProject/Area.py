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
        print(f"Area: {self.areaName} - {self.areaRef}")

    def parse_area_list(self, areaList):
        # create the area obj
        for i in range(1, len(areaList)):
            key = self.trailKeys[i]
            areaJson = areaList[i]
            areaObj = Area(areaJson["name"], areaJson["item"]) 
            self.trailMap[key] = areaObj

        return self.trailMap