import streamlit as st
import numpy as np
import time

st.markdown("# Trail Details")
st.write(
    """This demo illustrates trail details in Streamlit. 
    This will use query params to generate trail details. 
    """
)
st.markdown("## Trail params")
st.write(st.query_params)
