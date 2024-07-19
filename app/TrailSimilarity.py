from difflib import SequenceMatcher
import re

def similar(x, y):
    return SequenceMatcher(None, x, y).ratio()

# testing out string and id similarity
trailMap = {}
trailIds = ['Jones Creek', 'Goulding Creek', 'Mesa Connector', 'Intermediate Downhill', 'Meadow Beginner Downhill', 'Meadow Intermediate Downhill', 'Telegraph Connect', 'Bonus Trail', "Brown's Ridge: Jump Line", "Jump Line on Brown's Ridge", "Downhill (Durango Mesa Park)"]

count = 0
for trailId in trailIds:
    trailMap[trailId] = trailId 
    count += 1
print("TrailMap:")
print(trailMap)
print("\n")

openAITrails = ['1. **Intermediate Downhill (Durango Mesa Park)**', '2. **Meadow Intermediate Downhill**', "3. **Brown's Ridge: Jump Line**", "4. **Jump Line on Brown's Ridge**"] 

# find trails associated with open ai trails
orderedTrailMap = {}
missingTrails = []
simMap = {}
for trailId in trailIds:
    matching = [aiTrail for aiTrail in openAITrails if trailId in aiTrail]
    print(f"Trail id = {trailId}")
    if len(matching) == 1:
        match = matching[0] 
        print("Matching 1:")
        print(match)
        if match in simMap:
            print("Match in simMap:")
            sim = similar(trailId, match)
            simMap[match][trailId] = sim
            print(simMap)
        else:
            rank = int(re.findall(r'\d+', matching[0])[0])
            orderedTrailMap[rank] = {}
            orderedTrailMap[rank]["route_name"] = trailMap.pop(trailId)
        print("\n")
    elif len(matching) > 1:
        for match in matching:
            simMap[match] = {} 
            sim = similar(trailId, match)
            simMap[match][trailId] = sim
        print("Sim match > 1:")
        print(simMap)
        print("\n")
    else:
        # if no matching exists then add to missing list 
        missingTrails.append(trailMap.pop(trailId))
        print("No matches:")
        print(missingTrails)
        print("\n")

# update the ordered map with max items
print("--------------------------------")
print("Final Similar Map:")
for (key,val) in simMap.items():
    maxItem = max(val, key=val.get) 
    orderedTrailIds = [obj["route_name"] for obj in orderedTrailMap.values()] 
    print(f"key = {key}")
    print(f"val = {val}")
    print(f"Max item = {maxItem} - {val[maxItem]}")
    print(f"Ordered trail ids len = {len(orderedTrailIds)}")
    print(orderedTrailIds)
    #if maxItem not in orderedTrailMap.values(): 
    if maxItem not in orderedTrailIds: 
        print("Max item not in ordered trail map") 
        print("Add max item to ordered map...") 
        rank = int(re.findall(r'\d+', key)[0])
        print(f"Rank = {rank}") 
        orderedTrailMap[rank] = {}
        orderedTrailMap[rank]["route_name"] = trailMap.pop(maxItem)
    print("\n")
print("--------------------------------")

# if we have any values left in the trail map update missing items
for trailObj in trailMap.values():
    missingTrails.insert(0, trailObj) 

print("Final Ordered trail map:")
print(orderedTrailMap)
print("--------------------------------")
print("\n")

print("Missing trails:")
print(missingTrails)
print("--------------------------------")
print("\n")

print("Updated trail map:")
print(trailMap)
print("--------------------------------")
print("\n")

# missing trails need to be appended to the ordered map
mapLen = len(orderedTrailMap)
start = mapLen+1
end = mapLen+len(missingTrails)+1
print(f"Start = {start}")
print(f"End = {end}")
for i in range(start, end):
    orderedTrailMap[i] = missingTrails.pop(0)

print(f"Final Ordered trail map (len = {len(orderedTrailMap)}):")
print(f"Total trail ids = {len(trailIds)}")
print(orderedTrailMap)
print("--------------------------------")
print("\n")
