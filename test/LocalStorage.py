import streamlit as st
from streamlit_local_storage import LocalStorage

localS = LocalStorage()

# print the methods of this obj
methods = [name for name in dir(localS) if callable(getattr(localS, name))]
print("Methods:")
print(methods)
print("\n")

x = [1, 2, 3]
print(x)
localS.setItem("x", x)
st.write("# Local Storage")
st.write(localS.getAll())
st.write(localS.getItem("x"))
localS.deleteAll()
st.write("## new storage")
st.write(localS.getAll())
