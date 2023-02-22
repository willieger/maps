# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:25:59 2023

@author: WGeraghty
"""

import io
import base64
import pandas as pd
import folium
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
import os

# Define the path to the folder containing the CSV files
path = 'c:/users/wgeraghty/csvs/'

# Load all the data into a single pandas DataFrame
df = pd.DataFrame()
for filename in os.listdir(path):
    if filename.endswith('.csv'):
        file_df = pd.read_csv(os.path.join(path, filename))
        file_df = file_df.dropna(subset=['latitude', 'longitude'])
        df = pd.concat([df, file_df])

# Group the data by location and sum the values for each column
agg_dict = {'name': 'first'}
for col in df.columns[3:]:
    agg_dict[col] = 'sum'
grouped = df.groupby(['latitude', 'longitude']).agg(agg_dict)

# Create a map centered on the average latitude and longitude
mean_lat = df["latitude"].mean()
mean_lon = df["longitude"].mean()
map_ = folium.Map(location=[mean_lat, mean_lon], zoom_start=10)

# Create a MarkerCluster for the data and add it to the map
marker_cluster = MarkerCluster().add_to(map_)

# Add markers to the cluster, and a pop-up with the pie chart to each marker
for i, row in grouped.iterrows():
    location = (i[0], i[1])
    values = row.values[1:]
    labels = row.index[1:].tolist()

    # Sort the values and labels in descending order
    sort_idx = values.argsort()[::-1]
    values = values[sort_idx]
    labels = [labels[i] for i in sort_idx]

    # Combine the remaining columns into an "other" category
    if len(values) > 6:
        other_values = sum(values[6:])
        other_label = "OTHERS"
        values = values[:6]
        labels = labels[:6]
        values = list(values) + [other_values]
        labels = labels + [other_label]

    # Get the title of the popup from the first column of the row
    title = row['name'].split()[0]
    title = ''.join(filter(str.isalpha, title))
    title = f'<b>{title}</b>'

    fig, ax = plt.subplots(figsize=(0.4, 0.4))
    ax.pie(values, labels=labels, radius=10, shadow=True, startangle=90, autopct='%1.1f%%')
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    img_encoded = base64.b64encode(img.read()).decode("utf-8")
    html = folium.Html(f'<body>{title}<br><img src="data:image/png;base64,{img_encoded}"></body>', script=True)
    popup = folium.Popup(html, max_width=2650)
    folium.Marker(location, popup=popup).add_to(marker_cluster)
    plt.close()

# Add a LayerControl to allow toggling of the marker cluster layer
folium.LayerControl().add_to(map_)

map_.save('combinedmap.html')
