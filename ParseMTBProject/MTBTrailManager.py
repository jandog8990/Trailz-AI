from MTBTrailUrlParser import MTBTrailUrlParser
from MTBJsonLineParser import MTBJsonLineParser

# This is the main mtb trails parser that uses the following files:
# 1. MTBJsonLineParser.py - parses the json lines file
# 2. MTBTrailUrlParser.py - parses each individual URL
# 2. MTBTrailParser.py - parses the actual trail html page

# TODO: Need to loop through the json lines file and start parsing url pages
# let's parse the json lines file to get all trail routes
jlFile = "mtbproject.jl"
jsonLineParser = MTBJsonLineParser()
trail_urls = jsonLineParser.parse(jlFile)
print(f"Trail urls len = {len(trail_urls)}")

# loop through the json lines and parse each individual URL
trailUrlParser = MTBTrailUrlParser()
trailDataTuples = []
for i in range(5):
    url = trail_urls[i]
    print(f"\nTrail url = {url}")
    trailDataTuples.append(trailUrlParser.parseTrail(url))

# TODO: Need to go through the tuples, the first element is stored as the 
# MTBTrailRoute (insertOne), and the second element is array of 
# MTBTrailRouteDescriptions (insertMany) 

# TODO: Will need to create a way to optimize the inserts as the parsing takes
# so much time that the latency could bring down the db connections

print(f"Trail data tuples len = {len(trailDataTuples)}")
for i in range(len(trailDataTuples)):
    print(trailDataTuples[i])
    print("\n")
