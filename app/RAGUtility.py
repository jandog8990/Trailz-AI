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
        
        return mtbRouteDetail

    # sort the results based on distance function
    def sort_distance(self, trail):
        distance_str = trail['trail_stats']['distance']['imperial']
        return float(re.findall("\\d+\\.\\d+", distance_str)[0])

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

        # extract the trail ids
        trailIds = list(trailMap.keys()) 
 
        # create the recommended trail list
        openAITrails = []
        for line in streamList:
            hasNum = bool(re.search(r'\d.', line))
            if hasNum:
                trailSplit = re.split("\\*\\*", line)
                trailXX = trailSplit[0].strip() 
                trailNum = trailXX[0] 
                trailLine = bool(re.search(r'\d', trailNum)) 
                if trailLine: 
                    trailName = trailXX + ' ' + ' '.join(trailSplit[1:len(trailSplit)-1]) 
                    openAITrails.append(trailName)

        # create the ordered trail map using open ai trails 
        orderedTrailMap = {}
        missingTrails = []
        similarityMap = {} 
        print("Trail ids = " + str(len(trailIds)))
        print(trailIds)
        print("\n") 
        for trailId in trailIds:
            matching = [aiTrail for aiTrail in openAITrails if re.sub('[^A-Za-z0-9]+', '', trailId)
                        in re.sub('[^A-Za-z0-9]+', '', aiTrail)]
            if len(matching) == 1: 
                match = matching[0] 
                
                # if we have a match in similarity map -> update map
                if match in similarityMap:
                    sim = self.similar(trailId, match)
                    similarityMap[match][trailId] = sim
                else:
                    # if match -> ordered trail map will contain the objs 
                    rank = int(re.findall(r'\d+', matching[0])[0])
                    if rank not in orderedTrailMap: 
                        orderedTrailMap[rank] = trailMap.pop(trailId) 
                    else:
                        missingTrails.insert(0, trailMap.pop(trailId));
            elif len(matching) > 1:
                # update the similarity map with all match scores 
                for match in matching:
                    similarityMap[match] = {}
                    sim = self.similar(trailId, match)
                    similarityMap[match][trailId] = sim
            else:
                # get the index of the non-mathing elem
                missingTrails.append(trailMap.pop(trailId));

        print("Missing trails len = " + str(len(missingTrails)))
        for trail in missingTrails:
            print("missing trail id = " + trail["_id"]) 
        print("\n")
        
        # update the ordered map with max items in similarity map
        for (key, val) in similarityMap.items():
            maxItemId = max(val, key=val.get)
            orderedTrailIds = [obj["route_name"] for obj in orderedTrailMap.values()] 
            if maxItemId not in orderedTrailIds:
                rank = int(re.findall(r'\d+', key)[0])
                orderedTrailMap[rank] = trailMap.pop(maxItemId)

        # left over trail map values will be added to missing list
        for trailObj in trailMap.values():
            missingTrails.insert(0, trailObj)

        # The missing trails will need to be appended in order to the map 
        mapLen = len(orderedTrailMap) 
        start = mapLen+1
        end = mapLen+len(missingTrails)+1
        for i in range(start, end):
            orderedTrailMap[i] = missingTrails.pop(0)
        
        # if we are missing certain trail ids we need to ensure to remove
        print("Ordered trail map len = " + str(len(orderedTrailMap)))
        for (key, val) in orderedTrailMap.items():
            print("key = " + str(key))
            print("val route name = " + val["route_name"])
            print("\n")
        
        return orderedTrailMap 
