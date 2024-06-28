import gpxpy
#import gpxpy.gpx

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

#f = "coyote-chamisoso.gpx"
f = "north-table-co.gpx" 
with open(f, 'r') as gpxf:
    gpx = gpxpy.parse(gpxf)
    print(gpx.get_track_points_no()) 
    print(gpx.get_elevation_extremes()) 
    print(gpx.get_uphill_downhill()) 
    print(gpx.to_xml()[:1000]) 
segment = gpx.tracks[0].segments[0]
print("Segment:")
print(segment)
print("\n")
print(segment.points[:10])
print("\n")

print("Waypoints:")
print(f"len ways = {len(gpx.waypoints)}")
for waypoint in gpx.waypoints:
    print(waypoint) 
print("\n")

print("Routes:")
for route in gpx.routes:
    print('Route:')
    for point in route.points:
        print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevtion}')

# loop through segments and extract lat/lon
route_info = []
print("GPX Tracks:") 
for track in gpx.tracks:
    print(f"segments len = {len(track.segments)}") 
    print(f"track = {track}") 
    for segment in track.segments:
        print(f"points len = {len(segment.points)}") 
        for point in segment.points:
            print(f"point = {point}") 
            route_info.append({
                'latitude': point.latitude,
                'longitude': point.longitude,
                'elevation': point.elevation
            })
print("\n")
print("Route info:")
print(route_info[:3])
print("\n")

route_df = pd.DataFrame(route_info)
print(route_df.head())
route_df.to_csv("north-table-co.csv", index=False)

"""
plt.figure(figsize=(14, 8))
plt.scatter(route_df['longitude'], route_df['latitude'], color='#101010')
plt.title("Route lat and lon points", size=20)
plt.show()
"""
