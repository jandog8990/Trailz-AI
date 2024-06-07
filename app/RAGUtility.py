import streamlit as st
from TrailMongoDB import TrailMongoDB
from MTBTrailCreator import MTBTrailCreator

# RAG utility class for config and extra work
class RAGUtility:
    def __init__(self):
        print("RAGUtility.init()...") 
        self.mongoDB = TrailMongoDB() 
    
    # get the final results using MongoDB query 
    def query_mongodb_data(self, results):
        # NOTE: This gets data from the mainText and metadata of the PC PKL file 
        #return self.loadData.get_final_results(results, self.metadataSet)
        
        trailCreator = MTBTrailCreator()
        trail_ids = [obj['id'] for obj in results['matches']]

        # query the mongodb for trail routes/descriptions
        (trailRoutes, trailDescs) = self.mongoDB.find_mtb_trail_data_by_ids(trail_ids)

        # create the main mtb routes from the trail data
        mainMTBRoutes = trailCreator.create_mtb_routes(trailRoutes, trailDescs)

        return mainMTBRoutes 

    # Results is a list of trail contexts from the VectorDB
    def parse_rag_contexts(self, results):
        # TODO: sort depending on if the user specified a trail difficulty (if not sort on rating)

        # TODO: parse the results from the MongoDB and sort based on difficulty and rating if user specifies
        final_results = self.query_mongodb_data(results)
        final_results = sorted(final_results, key=lambda x: x['average_rating'], reverse=True)

        # send the contexts of main text to RAG
        contexts = [x['mainText'] for x in final_results]

        # set the trail map for contexts and  
        return (contexts, final_results)

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
            "I'm a personal assistant, I don't like to talk politics."

        define bot answer porn
            "I'm a personal assistant, I don't like to talk of porn."

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
