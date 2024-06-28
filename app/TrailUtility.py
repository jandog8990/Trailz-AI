import gpxpy
import pandas as pd
import requests
#import urllib.request

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
      
    # parse gpx file for route info
    def parse_gpx_file(self, gpx_file):
        route_info = [] 
        query_parameters = {"downloadformat": "xml"}
        #response = requests.get(gpx_file, params=query_parameters)
        #urllib.request.urlretrieve(gpx_file, "tmp.gpx") 
        #print(f"GPX = {gpx_file}") 
        #with open("tmp.gpx", "wb") as file:
        #    file.write(response.content)
        #print("gpx file donwloaded\n")
        #data = urllib2.urlopen(gpx_file).read()
        #soup = BeautifulSoup(data)
        #print(soup)

        #with open(gpx_file, 'r') as gpxf:
        #    gpx = gpxpy.parse(gpxf)
        """ 
        gpx = gpxpy.parse(response.content)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    route_info.append({
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'elevation': point.elevation
                    })
        return pd.DataFrame(route_info)
        """
        return None
