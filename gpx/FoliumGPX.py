import folium
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
from IPython.display import display
from IPython.display import Image 

route_df = pd.read_csv("coyote-chamisoso.csv")
route_df.head()

route_map = folium.Map(
    location=[45.79757947, 15.9007929],
    zoom_start=13,
    tiles='OpenStreetMap',
    width=1024,
    height=600)
display(route_map)
