from difflib import SequenceMatcher
import re

def similar(x, y):
    return SequenceMatcher(None, x, y).ratio()



# testing out string and id similarity
trailMap = {}
#trailIds = ['Pinkerton-Flagstaff Trail #522', 'Stevens Creek Trail #728', 'Jones Creek', 'Haflin Creek Trail', 'Goulding Creek', 'Intermediate Downhill', 'Sailing Hawks', 'Meadow Beginner Downhill', 'Meadow Intermediate Downhill', 'Telegraph Connect', "Brown's Ridge: Jump Line", "Jump Line on Brown's Ridge"]
#trailIds = ['Jones Creek', 'Goulding Creek', 'Mesa Connector', 'Intermediate Downhill', 'Meadow Beginner Downhill', 'Meadow Intermediate Downhill', 'Telegraph Connect', 'Bonus Trail', "Brown's Ridge: Jump Line", "Jump Line on Brown's Ridge", "Downhill (Durango Mesa Park)"]
trailIds = ['Pinkerton-Flagstaff Trail #522', 'Stevens Creek Trail #728', 'Jones Creek', 'Mesa Connector', 'Intermediate Downhill', 'Meadow Beginner Downhill', 'Meadow Intermediate Downhill', 'Telegraph Connect', "Brown's Ridge: Jump Line", "Jump Line on Brown's Ridge"]


count = 0
for trailId in trailIds:
    trailMap[trailId] = trailId 
    count += 1
print("TrailMap:")
print(trailMap)
print("\n")

streamList = ["1. **Meadow Intermediate Downhill** - This trail is professionally built specifically for downhill riding, featuring a series of moderately sized jumps and berms. It’s rated as Intermediate, making it suitable for riders with some experience looking for a fun, engaging ride. The trail’s design ensures consistent jumps with armored lips and lacks natural escape routes, which adds to the thrill and challenge.", "2. **Intermediate Downhill at Durango Mesa Park** - A newer addition, this trail features a lengthy series of large and medium-sized jumps, tabletops, and berms. It's slightly more challenging than the Meadow Intermediate Downhill, making it perfect for riders looking for a bit more thrill. The trailside trees and steep hillside add an element of challenge, making it essential to ride cautiously until you're familiar with the features.", "3. **Brown's Ridge: Jump Line** - Located in Overend Mountain Park, this trail is a local favorite, featuring a small jump line with rollable doubles and great berms. It's been recently reshaped, enhancing the fun factor. The trail is rated as Intermediate and offers a quick, enjoyable loop that you can ride multiple times to really get a feel for the jumps.", "4. **Jump Line on Brown’s Ridge** - This is a continuation of the Brown's Ridge Jump Line and offers a few more smaller, rollable doubles. It's perfect for looping back for more fun on the main Brown's Ridge Trail, making it an excellent choice for those looking to practice and perfect their jumping and berm-riding skills."]
#streamList = ['1. **Intermediate Downhill (Durango Mesa Park)**', '2. **Meadow Intermediate Downhill**', "3. **Brown's Ridge: Jump Line** and **Jump Line on Brown's Ridge**", "4. **Meadow Beginner Downhill**"] 
#openAITrails = ['1. Meadow Beginner Downhill', "2. Brown's Ridge: Jump Line", '3. Intermediate Downhill', '4. Meadow Intermediate Downhill']

# create the recommended trail list
openAITrails = []
for line in streamList:
    hasNum = bool(re.search(r'\d.', line))
    if hasNum:
        #if ":" in line:
        #    trailName = line.split(":")[0]
        #    openAITrails.append(trailName)
        #else:
        print(f"Line has num:") 
        trailSplit = re.split("\*\*", line)
        trailXX = trailSplit[0].strip() 
        trailNum = trailXX[0] 
        trailLine = bool(re.search(r'\d', trailNum)) 
        print(line) 
        print(f"trail num = {trailNum}") 
        print(f"trail XX = {trailXX}") 
        print(f"is trail line = {trailLine}") 
        print(trailSplit)
        if trailLine: 
            print("This is a trail line --- add") 
            trailName = trailXX + ' ' + ' '.join(trailSplit[1:len(trailSplit)-1]) 
            print(f"trial name = {trailName}") 
            print("\n")
            openAITrails.append(trailName)
            #openAITrails.append(line)
print(f"Open AI Trails (len = {len(openAITrails)}):")
print(openAITrails)
print("\n")

# find trails associated with open ai trails
orderedTrailMap = {}
missingTrails = []
simMap = {}
for trailId in trailIds:
    matching = [] 
    #matching = [aiTrail for aiTrail in openAITrails if trailId in aiTrail]
    print(f"Trail id = {trailId}")
    for aiTrail in openAITrails:
        if re.sub('[^A-Za-z0-9]+', '', trailId) in re.sub('[^A-Za-z0-9]+', '', aiTrail):
            matching.append(aiTrail)
    print(f"matching = {matching}")
    if len(matching) == 1:
        match = matching[0] 
        print("Matching len == 1:")
        print(match)
        
        if match in simMap:
            print("Match in simMap:")
            sim = similar(trailId, match)
            simMap[match][trailId] = sim
            print(simMap)
        else:
            print(f"NO Match in simMap:") 
            rank = int(re.findall(r'\d+', matching[0])[0])
            if rank not in orderedTrailMap: 
                orderedTrailMap[rank] = {}
                orderedTrailMap[rank]["route_name"] = trailMap.pop(trailId)
                print(f"Add Rank = {rank}")
                print(f"Trail map pop trailId = {trailId}")
            else:
                print(f"Rank {rank} exists -> skipping {trailId}")
                missingTrails.insert(0, trailMap.pop(trailId)) 
                #missingTrails.append(trailMap.pop(trailId));
                print(missingTrails)
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
print(f"Similarity map len = {len(simMap)}")
print("Final Similar Map:")
for (key,val) in simMap.items():
    maxItem = max(val, key=val.get) 
    orderedTrailIds = [obj["route_name"] for obj in orderedTrailMap.values()] 
    print(f"key = {key}")
    print(f"val = {val}")
    print(f"Max item = {maxItem} - {val[maxItem]}")
    print(f"Ordered trail ids len = {len(orderedTrailIds)}")
    #print(orderedTrailIds)
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
print("Add missing trails to ordered map:")
print(f"Start = {start}")
print(f"End = {end}")
for i in range(start, end):
    orderedTrailMap[i] = missingTrails.pop(0)

print(f"Final Ordered trail map (len = {len(orderedTrailMap)}):")
print(f"Total trail ids = {len(trailIds)}")
print(orderedTrailMap)
print("--------------------------------")
print("\n")
