import streamlit as st
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

    def get_rag_config(self):
        # the RAG config for LLMRails 
        yaml_content = """
        models:
        - type: main
          engine: openai
          model: gpt-4-turbo
        """

        # colang content for defining boundaries and return vars 
        rag_colang_content = """
        # define RAG boundaries for Q/A 
        define user ask porn
            "what do you think about porn?"
            "thoughts on sex?"
            "sexual"
            "lust"

        define user ask politics
            "what are your political beliefs?"
            "thoughts on the president?"
            "left wing"
            "right wing"

        define bot answer politics
            "I'm a personal trail assistant, I don't like to talk politics. Please ask me about trails you may be interested in discovering!"

        define bot answer porn
            "I'm a personal trail assistant, I don't like to talk porn. Please ask me about trails you may be interested in discovering!"

        define flow politics
            user ask politics
            bot answer politics
            bot offer help

        define flow porn
            user ask porn
            bot answer porn
            bot offer help
        
        # define RAG intents and flow
        define user ask mtb
            "find mtb trails"
            "trails with"
            "trails"
            "find trails"
            "steep trails"
            "flow"
            "easy"
            "intermediate"
            "advanced"
            "difficult"
            "tech"
            "techy"
            "mtb"
            "mtb trails"
            "what are some good mtb trails?"
            "where are some steep mtb trails?"
            "tell me about some good trails"
            "where are some flowy mtb trails?"
            "intermediate mtb trails"
            "advanced mtb trails"

        define flow mtb
            user ask mtb
            $trail_tuple = execute retrieve(query=$last_user_message, conditions=$conditions)
            $answer = execute rag(query=$last_user_message, trail_tuple=$trail_tuple) 
            bot $answer
        """
    
        return (yaml_content, rag_colang_content)
