# master-thesis-pprp

## vrptw-approaches/
* sample_data.py: some example datasets for playing with the algorithms
* vrptw_CP.py: simple implementation example using the **OR-TOOLS CP** solver
* vrptw_gurobi.py: simple implementation example using the **GUROBI** solver
* vrptw_metaheuristic.py: simple implementation example using the **OR-TOOLS metaheuristics** solver
* vrptw_mip.py: simple implementation example using the **OR-TOOLS LP** solver


## osmnx-example/
* download_map.py: example how map data can be downloaded 
* favoriten.osm: the downloaded map data
* example_map.py: example how to plot a map
* calculate_matrices.py: <span style="color:red">*Caution: needs currently almost an hour to run!*</span> takes favoriten.osm file and generates favoriten_data.py; many sub-routes are calculated repeatedly &rarr; could be made way more efficient if needed
* favoriten_data.py: <span style="color:red">*Caution: relatively huge file!*</span> used for saving the time_matrix, the distance_matrix, the osm_to_index hashtable, the index_to_osm hashtable, edges information and unusable nodes (bad_nodes)

