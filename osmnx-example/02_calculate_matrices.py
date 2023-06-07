"""*Caution: needs currently almost an hour to run!*
takes favoriten.osm file and generates favoriten_data.py"""

import os
import time
import osmnx as ox


start_time = time.time()
working_directory = os.path.dirname(os.path.abspath(__file__)) + "/"

# load map data
G = ox.io.load_graphml(filepath=working_directory+'favoriten.osm')

# hash tables
index_to_osm = dict(enumerate(G.nodes()))
osm_to_index = {val: key for key, val in index_to_osm.items()}

# counting which maxspeed values are given as list,
# as single value or not at all
c_list = 0
c_value = 0
c_nan = 0

# save length, distance and maxspeed data for all edges
edges = dict()

for edge in G.edges():
    edges[edge] = dict()
    start, end = edge
    edges[edge]['length'] = G[start][end][0]['length']

    if 'maxspeed' in G[start][end][0]:
        if isinstance(G[start][end][0]['maxspeed'], list):
            edges[edge]['maxspeed'] = int(min(G[start][end][0]['maxspeed']))
            c_list += 1
        else:
            # 'AT:zone:30' values can appear
            edges[edge]['maxspeed'] = int(G[start][end][0]['maxspeed'].split(':')[-1])
            c_value += 1
    else:
        edges[edge]['maxspeed'] = 30
        c_nan += 1

# collecting some information for statistics..
print(f"Total number of maxspeed values given as list: {c_list} (lowest is taken)")
print(f"Total number of maxspeed values given as single value: {c_value}")
print(f"Total number of missing maxspeed values: {c_nan} (30km/h is assumed)")
print(
    f"Does the sum equals the number of edges?: {c_list + c_value + c_nan == G.number_of_edges()}")

# calculate travel time for all edges
for edge in edges:
    start, end = edge
    edges[edge]['travel_time'] = round(edges[edge]["length"]/(edges[edge]['maxspeed']/3.6))

    # needs to be added for finding shortest route
    G[start][end][0]['travel_time'] = edges[edge]['travel_time']


# initialize matrices, number of nodes = 1272, each matrix includes 1.617.984 values
distance_matrix = [[0 for i in range(G.number_of_nodes())]
                   for j in range(G.number_of_nodes())]
time_matrix = [[0 for i in range(G.number_of_nodes())]
               for j in range(G.number_of_nodes())]


# for counting the impossible routes
impossible_routes = 0


for start in G.nodes():
    start_index = osm_to_index[start]
    for end in G.nodes():
        if start == end:
            continue
        end_index = osm_to_index[end]

        try:
            # weight: edge attribute to minimize when solving shortest path.
            # default is edge length in meters.
            # uses 'dijkstra'
            route = ox.shortest_path(G, start, end, weight='travel_time')

            distance_matrix[start_index][end_index] = sum(
                [edges[(s, e)]['length'] for s, e in zip(route[:-1], route[1:])])
            time_matrix[start_index][end_index] = sum(
                [edges[(s, e)]['travel_time'] for s, e in zip(route[:-1], route[1:])])

        except:
            distance_matrix[start_index][end_index] = None
            time_matrix[start_index][end_index] = None
            impossible_routes += 1


print(f"number of impossible routes: {impossible_routes}")


# collect the 'bad' nodes, which result in impossible routes
bad_nodes = set()

# checking the rows if there are many impossible routes
for i, row in enumerate(time_matrix):
    row_count = 0
    for j, item in enumerate(row):
        if item is None:
            row_count += 1
    if row_count > len(time_matrix)//2:
        bad_nodes.add(i)


# checking the colums if there are many impossible routes
for j in range(len(time_matrix)):
    column_count = 0
    for i in range(len(time_matrix)):
        if time_matrix[i][j] is None:
            column_count += 1
    if column_count > len(time_matrix)//2:
        bad_nodes.add(j)

print(f"The 'bad' nodes are: {bad_nodes}")
print(f"The count of bad nodes is: {len(bad_nodes)}")


# create a dictionary for the bad_nodes
index_to_removed_osm = {key: val for key, val in index_to_osm.items() if key in bad_nodes}

# remove the bad nodes from the data
remaining_nodes = [index_to_osm[i] for i in range(len(time_matrix)) if i not in bad_nodes]
index_to_osm = dict(enumerate(remaining_nodes))
osm_to_index = {val: key for key, val in index_to_osm.items()}


# initialize new time and distance matrices
cleaned_distance_matrix = [[0 for i in range(len(distance_matrix)-len(bad_nodes))]
                           for j in range(len(distance_matrix)-len(bad_nodes))]
cleaned_time_matrix = [[0 for i in range(len(time_matrix)-len(bad_nodes))]
                       for j in range(len(time_matrix)-len(bad_nodes))]

# fill the new matrices
row = 0
for i in range(len(distance_matrix)):
    if i in bad_nodes:
        continue
    column = 0
    for j in range(len(distance_matrix)):
        if j in bad_nodes:
            continue
        cleaned_distance_matrix[row][column] = distance_matrix[i][j]
        cleaned_time_matrix[row][column] = time_matrix[i][j]
        column += 1
    row += 1

del time_matrix
del distance_matrix

print("The new dimensions of the time_matrix are:" + \
    f"{len(cleaned_time_matrix)}x{len(cleaned_time_matrix)}")


ox.io.save_graphml(G, filepath=working_directory+'map_data.osm')

# save the data to file
with open(working_directory+'data_favoriten.py', 'w') as f:
    f.write(f'index_to_osm={index_to_osm}\n\n')
    f.write(f'osm_to_index={osm_to_index}\n\n')
    f.write(f'index_to_removed_osm={index_to_removed_osm}\n\n')
    f.write(f'edges={edges}\n\n')
    f.write(f'bad_nodes={bad_nodes}\n\n')
    f.write(f'distance_matrix={cleaned_distance_matrix}\n\n')
    f.write(f'time_matrix={cleaned_time_matrix}\n\n')


print(f'needed time: {time.time() - start_time}')
