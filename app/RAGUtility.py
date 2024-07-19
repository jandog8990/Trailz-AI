from TrailMongoDB import TrailMongoDB
from MTBTrailCreator import MTBTrailCreator
from difflib import SequenceMatcher
import re

# RAG utility class for config and extra work
class RAGUtility:
    def __init__(self):
        self.mongoDB = TrailMongoDB() 
        self.trailCreator = MTBTrailCreator()
    
    # get the final results using MongoDB query using trail metadata 
    def query_mongodb_trail_list(self, trail_ids):

        # query the mongodb for trail routes/descriptions
        (trailRoutes, trailDescs) = self.mongoDB.find_mtb_trail_data_by_ids(trail_ids)

        # create the main mtb routes from the trail data
        mainMTBRoutes = self.trailCreator.create_mtb_routes(trailRoutes, trailDescs)

        return mainMTBRoutes 

    # get trail route based on given ID
    def query_mongodb_trail_detail(self, trail_id):
        # query the mongodb for trail routes/descriptions
        (trailRoutes, trailDescs) = self.mongoDB.find_mtb_trail_data_by_ids([trail_id])
      
        trailRoute = trailRoutes[0]
        
        mtbRouteDetail = self.trailCreator.create_mtb_route_detail(trailRoute, trailDescs)
        #print("MTB Trail Route detail:")
        #print(mtbRouteDetail)
        #print("\n")
        
        return mtbRouteDetail

    # sort the results based on distance function
    def sort_distance(self, trail):
        distance_str = trail['trail_stats']['distance']['imperial']
        return float(re.findall("\d+\.\d+", distance_str)[0])

    # find similarity between two strings
    def similar(self, x, y):
        return SequenceMatcher(None, x, y).ratio()

    # Results is a list of trail contexts from the VectorDB
    def query_trail_list(self, trail_ids):

        # parse/sort results from MongoDB based on route distance 
        trail_list = self.query_mongodb_trail_list(trail_ids)
        trail_list = sorted(trail_list, key=self.sort_distance, reverse=True)
         
        return trail_list

    # sort the incoming trail list using stream output
    def sort_trail_map(self, trail_list, stream_output):
        # split the stream output based on new lines 
        streamList = stream_output.splitlines()
     
        # create the trail map from the trail list 
        trailMap = {obj["route_name"] : obj for obj in trail_list} 
        print("Original Trail Map:")
        for (key,val) in trailMap.items():
            print(f"key = {key}")
            print(f"val _id = {val['_id']}")
        print("\n")

        # extract the trail ids
        trailIds = list(trailMap.keys()) 
        print(f"Trail IDs (len = {len(trailIds)}):")
        print(trailIds)
        print("\n")

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

        # create the ordered trail map using open ai trails 
        orderedTrailMap = {}
        missingTrails = []
        similarityMap = {} 
        for trailId in trailIds:
            print(f"Trail id = {trailId}") 
            matching = [trail for trail in openAITrails if trailId in trail]
            print(f"Matching (len = {len(matching)}):")
            print(matching)
            print("\n")
            if len(matching) == 1: 
                match = matching[0] 
                print("Matching len == 1:")
                print(match)
                
                # if we have a match in similarity map -> update map
                if match in similarityMap:
                    print("match in similarityMap:")
                    sim = self.similar(trailId, match)
                    similarityMap[match][trailId] = sim
                    print("similarityMap:") 
                    print(similarityMap)
                else:
                    print("match NOT in simMap:") 
                    # if match -> ordered trail map will contain the objs 
                    rank = int(re.findall(r'\d+', matching[0])[0])
                    if rank not in orderedTrailMap: 
                        orderedTrailMap[rank] = trailMap.pop(trailId) 
                        print(f"Rank = {rank}")
                        print(f"Trail map pop trailId = {trailId}")
                        print(f"OrderTrailMap[{rank}] _id = {orderedTrailMap[rank]['_id']}")
                    else:
                        print(f"Rank {rank} exists -> skipping {trailId}")
                print("\n")
            elif len(matching) > 1:
                # update the similarity map with all match scores 
                for match in matching:
                    similarityMap[match] = {}
                    sim = self.similar(trailId, match)
                    similarityMap[match][trailId] = sim
                print("Sim match > 1:")
                print(similarityMap)
                print("\n")
            else:
                # get the index of the non-mathing elem
                missingTrails.append(trailMap.pop(trailId));
                print("No matches:")
                print(f"Missing trails len = {len(missingTrails)}")
                print("\n")

        print(f"Similarity Map len = {len(similarityMap)}:")
        print(similarityMap)
        print("\n")

        # update the ordered map with max items in similarity map
        for (key, val) in similarityMap.items():
            maxItemId = max(val, key=val.get)
            orderedTrailIds = [obj["route_name"] for obj in orderedTrailMap.values()] 
            print(f"key = {key}")
            print(f"val = {val}")
            print(f"Max item = {maxItemId} - {val[maxItemId]}")
            print(f"Ordered trail ids len = {len(orderedTrailIds)}")
            print(orderedTrailIds)
            if maxItemId not in orderedTrailIds:
                print("Max item not in trail ids -> add")
                rank = int(re.findall(r'\d+', key)[0])
                print(f"Rank = {rank}")
                orderedTrailMap[rank] = trailMap.pop(maxItemId)
            print("\n")

        print(f"Remaining trail map len = {len(trailMap)}")
        print(trailMap.keys())
        print("\n")

        # left over trail map values will be added to missing list
        for trailObj in trailMap.values():
            missingTrails.insert(0, trailObj)

        print(f"Updated ordered trail map len = {len(orderedTrailMap)}:")
        print(orderedTrailMap.keys())
        print(f"Missing trails len = {len(missingTrails)}:")
        print("\n")

        # The missing trails will need to be appended in order to the map 
        mapLen = len(orderedTrailMap) 
        start = mapLen+1
        end = mapLen+len(missingTrails)+1
        print("Add missing trails to ordered map:") 
        print(f"Start = {start}")
        print(f"End = {end}")
        for i in range(start, end):
            print(f"Index i = {i}")
            orderedTrailMap[i] = missingTrails.pop(0)
            print(f"OrderTrailMap[{i}] _id = {orderedTrailMap[i]['_id']}")
            print("\n") 

        return orderedTrailMap 
