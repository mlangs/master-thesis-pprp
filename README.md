# master-thesis-pprp

## vrptw-approaches/
- sample_data.py: some example datasets for playing with the algorithms
- vrptw_CP.py: simple implementation example using the **OR-TOOLS CP** solver
- vrptw_gurobi.py: simple implementation example using the **GUROBI** solver
- vrptw_metaheuristic.py: simple implementation example using the **OR-TOOLS metaheuristics** solver
- vrptw_mip.py: simple implementation example using the **OR-TOOLS LP** solver


## osmnx-example/
### 01_download_map.py
- example how map data can be downloaded
- uses `osmnx` to download a `.osm` map file and saves it

#### favoriten.osm
- the downloaded map data

### 02_calculate_matrices.py
*Caution: needs currently almost an hour to run!* takes `favoriten.osm` file and generates `favoriten_data.py` and `map_data.osm`; many sub-routes are calculated repeatedly &rarr; could be made way more efficient if needed
- loads the map file
- creates `index_to_osm` and `osm_to_index` by numbering the nodes from the map
- creates an `edges` dictionary with 'length' and 'maxspeed' values (the minimum given maxspeed is used or 30km/h if no speed limit is given)
- calculates rounded travel times for all the edges and adds it to the dictionary `edges`
	- travel_time = round(length / (maxspeed/3.6) (in seconds))
- initializes `distance_matrix` and `time_matrix`
- for any possible starting node to any possible end node the distance (and the travel time) is calculated by adding up the partial distances (travel times) for the shortest path (calculated with dijkstra with the osmnx module) 
	 - the impossible routes are counted (nodes which are not connected)
	 - the distances are not rounded for the distance matrix (which can be used later to calculate the total travel distance)
- the bad nodes are counted (if more than half of the other nodes cannot be reached from a not, it is considered bad)
- new cleaned `time_matrix` and `distances_matrix` are created (without any of the bad nodes)
- the following data is saved to a `.py` file:
	- `index_to_osm` (cleaned)
	- `osm_to_index` (cleaned)
	- `index_to_removed_osm`
	- `edges`
	- `bad_nodes`
	- `distance_matrix` (cleaned)
	- `time_matrix` (cleaned)
- the `G` graph is saved to `map_data.osm` (updated with travel times)


#### data_favoriten.py
*Caution: relatively huge file!* used for saving the time_matrix, the distance_matrix, the osm_to_index hashtable, the index_to_osm hashtable, edges information and unusable nodes (bad_nodes)
- the used map data

#### map_data.osm
- the network graph updated with the travel times

### 03_example_map.py
- example how to plot a map
- loads a map from a `.osm` file
- prints a shortest path (using 'distance' as weight)

### 04_visualisations.py
- counts all distances and all travel times
- the count of diagonal zeros is removed from the `counted[0]` dictionary (time from place `x` to the same place `x`)
- plots the distance/travel times on the x axis and the count on the y axis
- prints a map showing the removed nodes

### 05_map_with_node_labels.py
- uses matplotlib to plot a map using a `.osm` file
- every node on the map is labelled with the node id (might take a few seconds to load)


## simulation/
### config.py
- the config file

### main.py
- the main file
- conducts the simulation

#### data_favoriten.py
- the map pre-processed map data

### mvf.py
-additional functions

#### map_data.osm
- the map data including added travel times

### vrptw_metaheuristic.py
- google or-tools functions
