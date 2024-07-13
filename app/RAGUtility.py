from TrailMongoDB import TrailMongoDB
from MTBTrailCreator import MTBTrailCreator
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
        print("MTB Trail Route detail:")
        print(mtbRouteDetail)
        print("\n")
        
        return mtbRouteDetail

    # sort the results based on distance function
    def sort_distance(self, trail):
        distance_str = trail['trail_stats']['distance']['imperial']
        return float(re.findall("\d+\.\d+", distance_str)[0])

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
                openAITrails.append(line)

        # create the ordered trail map using open ai trails 
        orderedTrailMap = {}
        missingTrails = []
        for id in trailIds:
            matching = [trail for trail in openAITrails if id in trail]
            if len(matching) > 0: 
                # if match -> ordered trail map will contain the objs 
                rank = int(re.findall(r'\d+', matching[0])[0])
                #foundIndex = trail_list.index({"route_name": id})
                #orderedTrailMap[rank] = key 
                #orderedTrailMap[rank] = trail_list[foundIndex] 
                orderedTrailMap[rank] = trailMap.pop(id) 
            else:
                # get the index of the non-mathing elem
                #missingIndex = trail_list.index({"route_name": id})
                #del trailObjs[missingIndex] 
                #missingTrails.append(trail_list.pop(missingIndex));
                missingTrails.append(trailMap.pop(id));

        print(f"Original trail ids (len = {len(trailIds)}):")
        print(trailIds)
        print("\n")
        
        print(f"Missing trails (len = {len(missingTrails)}):")
        print(missingTrails)
        print("\n") 
    
        print(f"Remaining trail map (len = {len(trailMap)}):") 
        print(trailMap)
        print("\n") 
         
        # The missing trails will need to be appended in order to the map 
        mapLen = len(orderedTrailMap) 
        start = mapLen+1
        end = mapLen+len(missingTrails)+1
        for i in range(start, end):
            orderedTrailMap[i] = missingTrails.pop(0)
       
        print("New ordered trail map:") 
        mapLen = len(orderedTrailMap) 
        print(f"New map len = {len(orderedTrailMap)}")
        for i in range(1, len(orderedTrailMap)+1):
            print(str(i) + ": " + str(orderedTrailMap[i]))
        print("\n") 
        
        return orderedTrailMap 