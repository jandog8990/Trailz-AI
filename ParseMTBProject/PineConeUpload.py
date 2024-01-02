import sys
from MTBTrailMongoDB import MTBTrailMongoDB 

mongoDB = MTBTrailMongoDB() 
routesDF = mongoDB.find_mtb_trail_routes()
descDF = mongoDB.find_mtb_trail_descriptions()
(routeDataFrames, descDataFrames) = mongoDB.find_mtb_trail_data()
print(f"Routes list len = {len(routesDF)}")
print(f"Descs list len = {len(descDF)}")
print("\n")
print(f"Routes link size = {len(routeDataFrames)}")
print(f"Descs link size = {len(descDataFrames)}")
print("\n")

"""
print(f"Routes df size = {len(routesDF.index)}")
print(f"Descs df size = {len(descDF.index)}")
print("\n")

print(routeDataFrames.head(5))
print(descDataFrames.head(5))
"""

"""
# let's look for ids outside of the trail routes
trailIds = [frame['_id'] for frame in routesDF]
print(f"Trail ids len = {len(trailIds)}")
print(trailIds)
print("\n")

# loop through descriptions and remove ids
missingIds = [desc['mtb_trail_route_id'] for desc in descDF 
    if desc['mtb_trail_route_id'] not in trailIds]
print(f"Missing ids len = {len(missingIds)}")
print(missingIds)
print("\n")

# find trail routes by ids
missingRoutes = mongoDB.find_mtb_trail_routes_by_ids(testIds)
print(f"Missing routes len = {len(missingRoutes)}")
print(missingRoutes)
print("\n")
"""

