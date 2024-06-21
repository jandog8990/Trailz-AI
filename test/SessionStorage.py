import streamlit as st
from streamlit_session_browser_storage import SessionStorage 

seshS = SessionStorage()

# print the methods of this obj
methods = [name for name in dir(seshS) if callable(getattr(seshS, name))]
print("Methods:")
print(methods)
print("\n")

x = [1, 2, 3]
y = {"a": 1, "b": 2, "c": 3}
print(x)
seshS.setItem("x", x, key="x")
seshS.setItem("y", y, key="y")
st.write("# Local Storage")
st.write(seshS.getAll())
st.write(seshS.getItem("x"))
st.write(seshS.getItem("y"))
seshS.deleteItem("y")
st.write("## new storage")
st.write(seshS.getAll())
