import streamlit as st
from MTBLoadDataset import MTBLoadDataset

# RAG utility class for config and extra work
class RAGUtility:
    def __init__(self):
        self.loadData = MTBLoadDataset()

    @st.cache_resource
    def load_dataset(_self):
        # load the metadata set for the final results
        print("Load Dataset...")
        _self.metadataSet = _self.loadData.load_dataset()

    # get the final results using mtb metadata
    def get_final_results(self, results):
        return self.loadData.get_final_results(results, self.metadataSet)
    
    def parse_contexts(self, results):
        # parse the results from PC into context vector 

        # TODO: Call the get final results func
        #self.get_final_results(results)

    def get_rag_config(self):
        # the RAG config for LLMRails 
        yaml_content = """
        models:
        - type: main
          engine: openai
          model: gpt-3.5-turbo-instruct
        """

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
            $contexts = execute retrieve(query=$last_user_message, conditions=$conditions)
            $answer = execute rag(query=$last_user_message, contexts=$contexts)
            bot $answer
        """
    
        return (yaml_content, rag_colang_content)
