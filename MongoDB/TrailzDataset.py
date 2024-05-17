from MTBTrailMongoDB import MTBTrailMongoDB 

trailMongoDB = MTBTrailMongoDB()
result = trailMongoDB.find_mtb_trail_data()
routeDataFrame = result[0]
descDataFrame = result[1]
print(f"Route data frame len = {len(routeDataFrame)}")
print(f"Route desc data frame len = {len(descDataFrame)}")

# create ids list
print(routeDataFrame.head())
print("\n")

print(descDataFrame.head())
print("\n")
