from TrailMongoDB import TrailMongoDB
from MTBTrailCreator import MTBTrailCreator
import re

# RAG utility class for config and extra work
class RAGUtility:
    def __init__(self):
        self.mongoDB = TrailMongoDB() 
        self.trailCreator = MTBTrailCreator()
    
    # get the final results using MongoDB query using trail metadata 
    def query_mongodb_trail_list(self, trail_metadata):
        # pull the trail ids from the metadata 
        trail_ids = [obj['route_id'] for obj in trail_metadata] 

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
    def query_trail_list(self, trail_metadata):

        # parse/sort results from MongoDB based on route distance 
        trail_list = self.query_mongodb_trail_list(trail_metadata)
        trail_list = sorted(trail_list, key=self.sort_distance, reverse=True)

        return trail_list

    # sort the incoming trail list using stream output
    def sort_trail_map(self, trail_list, stream_output):
        # split the stream output based on new lines 
        streamList = stream_output.splitlines()
        print(f"Stream list split (len = {len(streamList)}")
        print(streamList)
        print("\n")
        
        # create the recommended trail list
        openAITrails = []
        for line in streamList:
            hasNum = bool(re.search(r'\d.', line))
            if hasNum:
                openAITrails.append(line)
        print(f"OpenAI Recommended Trails (len = {len(openAITrails)}):")
        print(openAITrails)
        print("\n")
        
         
                