"""
downloading amenity data, adding nearest network nodes and saving it as .csv file
"""

from pathlib import Path
import statistics

import osmnx as ox
import pandas as pd


def get_nearest_node(x):
    """
    getting nearest node
    """
    if x.osmid in G.nodes():
        return x.osmid

    if x.geometry.startswith('POINT'):
        s = [long_lat.split(' ') for long_lat in x.geometry[7:-1].split(', ')]
    elif x.geometry.startswith('POLYGON'):
        s = [long_lat.replace('(', '').replace(')', '').split(' ')
             for long_lat in x.geometry[10:-2].split(', ')]
    elif x.geometry.startswith('MULTIPOLYGON'):
        s = [long_lat.replace('(', '').replace(')', '').split(' ')
             for long_lat in x.geometry[16:-3].split(', ')]
    elif x.geometry.startswith('LINESTRING'):
        s = [long_lat.split(' ') for long_lat in x.geometry[12:-1].split(', ')]

    longitudes = [float(long_lat[0]) for long_lat in s]
    latitudes = [float(long_lat[1]) for long_lat in s]
    longitude, latitude = statistics.mean(longitudes), statistics.mean(latitudes)

    # graph, longitude, latitude
    next_node = ox.distance.nearest_nodes(G, longitude, latitude, return_dist=False)
    return next_node


# so pandas does not hide columns in the terminal
pd.options.display.width = 0

path = Path(__file__).parent.absolute()

pois = ox.geometries_from_place('Favoriten, Wien, 1100, Österreich',
                                tags={'amenity': True})

# index=True saves also the osmid and the element type
df = pois[['amenity', 'name', 'geometry']]
df.to_csv(path / "pois.csv", index=True, header=True)

pois = pd.read_csv(path / 'pois.csv')

# getting network map
G = ox.io.load_graphml(filepath=path / 'map_data.osm')

# adding nearest_network_nodes to the dataframe
pois['nearest_network_node'] = pois.apply(get_nearest_node, axis=1)
# print(pois.head())

# saving dataframe
pois.to_csv(path / "pois_with nearest node.csv", index=False, header=True)
