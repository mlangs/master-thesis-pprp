"""example how map data can be downloaded """

import os
import osmnx as ox


working_directory = os.path.dirname(__file__) + "/"

# downlaod map
# G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')
G = ox.graph_from_place('Favoriten, Wien, 1100, Österreich', network_type='drive')

# plot
G_projected = ox.project_graph(G)
ox.plot_graph(G_projected)

# save map
ox.io.save_graphml(G, filepath=working_directory+'favoriten.osm')
