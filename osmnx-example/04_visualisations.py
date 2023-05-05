"""two simple plots to visualize the route lengths and route times"""

import os
import itertools
from collections import Counter
import matplotlib.pyplot as plt
import osmnx as ox
import data_favoriten as d


for matrix in [d.time_matrix, d.distance_matrix]:
    chained_matrix = [item for item in itertools.chain(*matrix)]

    counted = dict(Counter(chained_matrix))

    # remove diagonal zeros
    counted[0] -= len(matrix)
    # time matrix still countains 12 zeros
    print(f"Count of 0s which are not on the diagnonal: {counted[0]}")
    print(f"Maximum value: {max(chained_matrix)}")

    x = counted.keys()
    y = counted.values()
    plt.scatter(x, y, marker='.', s=1, c='r')

    plt.title('frequency')
    plt.show()

print()

working_directory = os.path.dirname(__file__) + "/"

# load map
G = ox.io.load_graphml(filepath=working_directory+'favoriten.osm')

fig, ax = ox.plot_graph(G, bgcolor='#999999', node_color='k',
                        edge_color='b', show=False, close=False)


for index in d.bad_nodes:
    x = G.nodes()[d.index_to_removed_osm[index]]["x"]
    y = G.nodes()[d.index_to_removed_osm[index]]["y"]
    ax.scatter(x, y, c='red')

ax.set_title('Favoriten: removed nodes')
plt.show()
