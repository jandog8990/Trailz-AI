from MTBJsonLineParser import MTBJsonLineParser
import time

# let's parse the json lines file to get all trail routes
jlFile = "../../mtb-project-crawler/mtbproject.jl"
st = time.time()
jsonLineParser = MTBJsonLineParser()
trail_map = jsonLineParser.parse_trailz(jlFile)
et = time.time()
elapsed = et - st
#trail_urls = trail_urls[0:5]
print(f"Json Line Parser time = {elapsed} sec")
print(f"Trail map len = {len(trail_map)}")
print("\n")

