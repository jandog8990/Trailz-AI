# init db utility objects
import streamlit as st
from RAGUtility import RAGUtility

print("Trail detail - Session state:")
print(st.session_state)
print("\n")
for k, v in st.session_state.to_dict().items():
    print(f"key = {k}") 
    st.session_state[k] = v

import numpy as np
import time

#from RAGUtility import RAGUtility

st.markdown("# Trail Details")
st.write(
    """This demo illustrates trail details in Streamlit. 
    This will use query params to generate trail details. 
    """
)
st.markdown("## Trail params")
st.write(st.query_params)
trail_id = st.query_params.id
print(f"Trail id = {trail_id}")
ragUtility = RAGUtility() 

ragUtility.query_mongodb_trail_detail(trail_id)
