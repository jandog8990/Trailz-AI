# Trail Utility is needed to build objects for the app
# this includes creating trail stats, images, etc.
class TrailUtility:
    # create trail stats from units 
    def createTrailStats(self, trailStats, units):
        distanceObj = trailStats['distance']
        elevationObj = trailStats['elevationChange']
        
        # check units and create string for 
        routeDetails = "" 
        if units == "Metric":
            distance = distanceObj['metric']
            metricUp = elevationObj['metricUp']
            metricDown = elevationObj['metricDown']
            routeDetails = distance + " - " + metricUp + " Up - " + metricDown + " Down" 
        else: 
            distance = distanceObj['imperial']
            imperialUp = elevationObj['imperialUp']
            imperialDown = elevationObj['imperialDown']
            routeDetails = distance + " - " + imperialUp + " Up - " + imperialDown + " Down" 
       
        return routeDetails 
