import os
import osmnx as ox
import matplotlib.pyplot as plt
import data_favoriten as d

working_directory = os.path.dirname(__file__) + "/"

# load map
G = ox.io.load_graphml(filepath=working_directory+'favoriten.osm')

bad_osm_nodes = [d.index_to_removed_osm[x] for x in d.bad_nodes]
possible_nodes = [node for node in G.nodes() if node not in bad_osm_nodes]


fig, ax = ox.plot_graph(G, bgcolor='#999999', node_color='k',
                        edge_color='b', show=False, close=False)

for index in G.nodes():
    if index in bad_osm_nodes:
        continue
    x = G.nodes()[index]["x"]
    y = G.nodes()[index]["y"]
    ax.scatter(x, y, c='red')
    plt.text(x, y, index, ha='left', rotation=15, wrap=True)

ax.set_title('Favoriten: node numbers')
plt.show()
