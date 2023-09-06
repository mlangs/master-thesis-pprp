"""
read simulation files and save relevant data to a .csv file
"""

import json
from pathlib import Path

import pandas as pd
import osmnx as ox

import data_favoriten as d


def get_data_from_file(file):
    """
    loads the file data
    """
    with open(file, 'r') as json_file:
        data = json.load(json_file)
    return data


def get_all_routes(data, G):
    """
    getting all routes with all extra steps
    """
    all_routes = []
    for v_id in data['vehicles']:
        route = data['vehicles'][v_id]['route']
        complete_route = []

        complete_route.append(route[0])
        for start, end in zip(route[:-1], route[1:]):
            partial_route = ox.shortest_path(G, start[0], end[0], weight='travel_time')

            for i, location in enumerate(partial_route[1:-1]):
                arrival_time = complete_route[-1][2] + \
                    d.time_matrix[d.osm_to_index[location]][d.osm_to_index[partial_route[1:][i+1]]]
                complete_route.append([location, arrival_time, arrival_time])
            complete_route.append(end)

        all_routes.append(complete_route)
    return all_routes


def main():
    """
    reads all the .json files and saves a .csv file
    """

    path = Path(__file__).parent.absolute()
    files = path.glob("output/*.json")

    file_count = len(list(files))
    print(f"file_count: {file_count}\n")

    data_dict = {# simulation seed
                 'seed': [],
                 # solution strategy for initial solution
                 'firstsolutionstategy': [],
                 # metaheuristic for local search
                 'localsearchmetaheuristic': [],
                 # solution limit for a search
                 'solution_limit': [],
                 # time limit for a search
                 'time_limit': [],
                 # time planned for patrolling in each location
                 'patrolling_time_per_location': [],
                 # total km of the network graph
                 # ignoring removed nodes and counting two-way roads only once
                 'total_km': [],
                 # how much time the simulation took
                 'calculation_time': [],
                 # number of police vehicles
                 'n_vehicles': [],
                 # number of visited patrol locations
                 'n_visited_patrol_locations': [],
                 # total number of available patrol locations
                 'n_patrol_locations': [],
                 # total number of emergencies
                 'n_emergencies': [],
                 # emergencies per police vehicle
                 'n_emergencies_per_vehicle': [],
                 # number of missed emergencies
                 'n_missed_emergencies': [],
                 # time spend at emergencies
                 'attended_emergency_time': [],
                 # total time needed for all emergencies
                 'total_emergency_time': [],
                 # effective travel times (patrolling, emergencies and driving,
                 # not the time at the police station)
                 'travel_times': [],
                 # total travel time summed up for all vehicles
                 'total_travel_time': [],
                 # travel distances for all vehicles as list [v1, v2, .. ]
                 'travel_distances': [],
                 # total travel distance summed up for all vehicles
                 'total_travel_distance': [],
                 # travel distance, but all raods are only counted once
                 # two-way roads are also only counted once
                 'unique_distance': [],
                 # unique_distance / total_km
                 'coverage': [],
                 # reaction time for attended emergencies
                 'reaction_times': []}


    G = ox.io.load_graphml(filepath=path / 'map_data.osm')

    removed_nodes = list(d.index_to_removed_osm.values())

    # total km (excluding removed nodes)
    # counting two-way roads only once
    added_edges = []
    total_m = 0
    for s, e in G.edges():
        # ignore removed nodes
        if s in removed_nodes or e in removed_nodes:
            continue
        # do not double count edges
        if (s, e) in added_edges or (G[s][e][0]['oneway'] is False and (e, s) in added_edges):
            continue
        total_m += G[s][e][0]['length']
        added_edges.append((s, e))


    for file in path.glob("output/*.json"):
        data = get_data_from_file(file)

        # seed
        data_dict['seed'].append(data['seed'])

        # solution strategy for initial solution
        data_dict['firstsolutionstategy'].append(data['firstsolutionstategy'])

        # metaheuristic for local search
        data_dict['localsearchmetaheuristic'].append(data['localsearchmetaheuristic'])

        # solution limit for a search
        data_dict['solution_limit'].append(data['solution_limit'])

        # time limit for a search
        data_dict['time_limit'].append(data['time_limit'])

        # time planned for patrolling in each location
        data_dict['patrolling_time_per_location'].append(data['patrolling_time_per_location'])

        # total_km of the network
        data_dict['total_km'].append(total_m / 1000)

        # calculation time
        data_dict['calculation_time'].append(data['calculation_time'])

        # number of vehicles
        data_dict['n_vehicles'].append(len(data['vehicles']))

        # number of visited patrol locations
        data_dict['n_visited_patrol_locations'].append(
            len([location for location in data['visited_locations']
                 if location in data['patrol_locations']]))

        # total number of available patrol locations
        data_dict['n_patrol_locations'].append(len(data['patrol_locations']))

        # total number of emergencies
        data_dict['n_emergencies'].append(len(data['emergencies']))

        # number of emergencies per police vehicle
        emergency_counts = []
        all_ids = [emergency['assigned_vehicle_id']
                   for emergency in data['emergencies'].values()]
        for v_id in range(len(data['vehicles'])):
            emergency_counts.append(all_ids.count(v_id))
        data_dict['n_emergencies_per_vehicle'].append(emergency_counts)

        # number of missed emergencies
        number_of_missed_emergencies = sum(emergency['assigned_vehicle_id'] is None
                                           for emergency in data['emergencies'].values())
        data_dict['n_missed_emergencies'].append(number_of_missed_emergencies)

        # time spent at emergencies
        time_at_emergencies = sum(emergency['duration']
                                  for emergency in data['emergencies'].values()
                                  if emergency['assigned_vehicle_id'] is not None)
        data_dict['attended_emergency_time'].append(time_at_emergencies)

        # total time for all emergencies
        total_emergency_time = sum(
            emergency['duration'] for emergency in data['emergencies'].values())
        data_dict['total_emergency_time'].append(total_emergency_time)


        # travel times and travel distances
        all_routes = get_all_routes(data, G)

        travel_times = []
        travel_distances = []
        added_edges = []
        unique_distance = 0 # for all vehicles

        # for each vehicle
        for route in all_routes:
            travel_time = 0
            travel_distance = 0
            for s, e in zip(route[:-1], route[1:]):
                # time travelling from node to node
                travel_time += d.time_matrix[d.osm_to_index[s[0]]][d.osm_to_index[e[0]]]

                # time at emergencies or time patrolling
                if s[0] != data['police_station']:
                    travel_time += s[2]-s[1]

                # distance travelling from node to node
                travel_distance += d.distance_matrix[d.osm_to_index[s[0]]][d.osm_to_index[e[0]]]

                # ignoring if already counted directly or
                # if counted the other way (for two-ways)
                if (s[0], e[0]) in added_edges or \
                ((e[0], s[0]) in added_edges and G[s[0]][e[0]][0]['oneway'] is False):
                    pass
                else:
                    unique_distance += d.distance_matrix[d.osm_to_index[s[0]]][d.osm_to_index[e[0]]]
                    added_edges.append((s[0], e[0]))

            if e[0] != data['police_station']:
                travel_time += s[2]-s[1]

            travel_times.append(travel_time)
            travel_distances.append(travel_distance)

        data_dict['travel_times'].append(travel_times)
        data_dict['total_travel_time'].append(sum(travel_times))
        data_dict['travel_distances'].append(travel_distances)
        data_dict['total_travel_distance'].append(sum(travel_distances))
        data_dict['unique_distance'].append(unique_distance)
        data_dict['coverage'].append(unique_distance / (1000*data_dict['total_km'][-1]))

        # reaction times for attended emergencies
        reaction_times = [emergency['arrival_time']-emergency['start_time']
                          for emergency in data['emergencies'].values()
                          if emergency['assigned_vehicle_id'] is not None]
        data_dict['reaction_times'].append(reaction_times)

    df = pd.DataFrame(data_dict)
    df.to_csv(path / 'favoriten.csv', index=False, header=True)

    # so pandas does not hide columns in the terminal
    pd.options.display.width = 0
    print(df.head())
    # print(df.describe())


if __name__ == '__main__':
    main()
