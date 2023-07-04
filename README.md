# master-thesis-pprp

## vrptw-approaches/
- sample_data.py: some example datasets for playing with the algorithms
- vrptw_CP.py: simple implementation example using the **OR-TOOLS CP** solver
- vrptw_gurobi.py: simple implementation example using the **GUROBI** solver
- vrptw_metaheuristic.py: simple implementation example using the **OR-TOOLS metaheuristics** solver
- vrptw_mip.py: simple implementation example using the **OR-TOOLS LP** solver


## osmnx-example/
shows how to retrieve openstreetmap data and how to prepare it for the simulation

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

### 06_get_amenity.py
- downloads amenity data
- removes unimportant columns and saves it as `pois.csv`
- uses longitude and latitute to add the nearest road network node to the dataframe
  if the amenity is not a point (linestring, polygon, multipolygon), the average coordinates are taken
- saves the dataframe as `pois_with nearest node.csv`

#### pois.csv
- the amenity dataframe (most of the columns are removed) 

#### pois_with nearest node.csv
- the `pois.csv` dataframe with the added `nearest_network_node` column

### 07_select_pois.py
- reads `pois_with nearest node.csv`
- prints a dictionary of all amenities
- prints all police stations and a list of their nearest network nodes
- takes a list of relevant tags
- removes entries where the nearest node is a removed node
- returns a sample of unique nodes with relevant tags


## simulation/
contains the actual simulation files and scripts to process the results 

### config.py
- the config file
- sets a `SEED_LIST`, the `NUMBER_OF_SIMULATIONS`, the number of simultaneous processes `MAX_WORKERS` and many other parameters

### main.py
- runs the simulation
- imports config, mvf, vrptw_metaheuristic and data_favoriten

#### data_favoriten.py
- the pre-processed map data

### mvf.py
contains functions for the simulation
- create_emergencies:
	creates and returns emergencies
- update_locations_and_windows:
	prepares the locations and time windows for the create_data_model function
	time windows need to get handled differently for different cases
	to force the correct behavior
- create_data_model:
	creates the data dictionary, which is needed for ortools
- update_patrol_locations_and_time_windows:
	removes visited patrol locations, removes patrol locations with missed time windows and adapts time windows
- Vehicle class:
	for keeping track of vehicle information
	- Vehicle.update:
		calculates current_location, time_to_curr_location, time_at_curr_location
	- Vehicle.update_current_route:
		does a backup of the route and updates it with the new route data
- choose_response_vehicle:
	returns the vehicle id of the response vehicle, the arrival time at the emergency and the departure_time after the emergency is dealt with
- update_vl:
	updates the visited locations list
- save_to_file:
	creates an output folder and saves the results there as a `{seed}.json` file

#### map_data.osm
- the map data including added travel times

### vrptw_metaheuristic.py
contains adapted google ortools functions
- print_solution:
	prints the solution to the console
- get_routes:
	formats the route data for further processing
- plan_routes:
	solves the VRP with time windows

### testing_unittest.py
- test_settings:
	some tests for the config parameters to make identifying configuration mistakes easier
- test_create_emergencies:
	creates 100 emergencies, asserts correct indexing and plausible results
- test_update_locations_and_windows:
	tests if the mvf.update_locations_and_windows function returns the correct starts, dummy_locations, updated_patrol_locations and time_windows
- test_create_data_model:
	tests if create_data_model return the correct data dictionary
- test_update_patrol_locations_and_time_windows:
	tests if new_patrol_locations and new_time_windows are updated correctly
- test_vehicle_class_update:
	tests if Vehicle.update returns the correct values for current_location, time_to_curr_location and time_at_curr_location
- test_vehicle_class_update_current_route:
	tests if the route is updated correctly
- test_choose_response_vehicle:
	a test for choosing a reponse vehicle (id, arrival time and return time needs to be correct)
- test_update_vl:
	tests if a location is correctly added to the visited_locations list

### testing_plausibility.py
- get_emergency_length_errors:
	returns the number of times the emergency duration is not equal to the end-arrival time
- get_emergency_time_errors:
	returns the number of times the emergency time order is wrong (arrival time before start time)
- get_missed_emergencies_errors:
	returns the number of missed events - number of extra vehicles, which should yield 0
- get_did_not_reach_police_station_errors:
	returns the number of times a vehicles is not at the police station when the simulation ends
- get_travel_time_errors:
	returns the number of times a vehicle is faster or slower than it is supposed to be according to the time matrix
-  get_time_order_errors:
	returns the number of times a vehicle leaves before it arrives
- get_wait_times_at_wrong_locations:
	looking only at locations, which are not a patrol location or the police station
	returns the difference between the time a vehicle spends waiting and attending emergencies (should be 0)
- get_visited_locations_duplicate_mismatch:
	returns the number of duplicates in the visited_locations list
- get_not_plausible_patrol_locations_visits:
	the number of all visited patrol locations + all emergencies at patrol locations needs to greater than all actual visits at patrol locations (emergency can happen after patrolling, no patrolling after emergency) 
- get_patrolling_time_errors:
	returns the number of times the the duration of a stay is not correct
	it is allowed to
	- stay at the police station
	- pass the location (0 time spend)
	- patrol at the location (exactly patrolling_time_per_location time spend, has to be a patrol location)
	- stay at a patrol location (time > 0), but leaving for an emergency
	- stay because there is currently an emergency (excactly the arrival and end time)
	- stay longer because an emergency appeared at the patrol location while patrolling
	if this criteria is not matched, there has to be a wrong time or wrong location

###  read_results.py
- reads the results and saves the processed data in `favoriten.csv`

#### favoriten.csv
- results of the simulations, can be imported as pandas dataframe
