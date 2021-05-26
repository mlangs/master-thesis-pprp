import os
import osmnx as ox
from pprint import pprint
import matplotlib.pyplot as plt


working_directory = os.path.dirname(__file__) + "/"

# load map
G = ox.io.load_graphml(filepath=working_directory+'favoriten.osm')

# just plot the map
# ox.plot_graph(G, bgcolor='#999999', node_color='k', edge_color='b')
# plt.show()

nodes = G.nodes()
edges = G.edges()
# print(type(G))
# print(G.nodes())
# pprint(G[17322882])
# print(G.nodes()[17322882])  # longitude and latitude
# print(type(edges))
# print(G.number_of_edges())
# print(edges)
# print(G[252281626][103657556])


origin_node = 17322882
destination_node = 103660646

# uses 'dijkstra'
route = ox.shortest_path(G, origin_node, destination_node, weight='length')
# print(route)

fig, ax = ox.plot_graph_route(G, route, bgcolor='#999999',
                              node_color='k', edge_color='b', route_color='r', show=False, close=False)
ax.set_title('Favoriten')
plt.show()
