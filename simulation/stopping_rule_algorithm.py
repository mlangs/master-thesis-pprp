import json
from pathlib import Path

import scipy.stats
import osmnx as ox

from main import main as run_simulation_batch
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


def get_calculation_time(data):
    return data['calculation_time']


def distances_and_times(data, G):
    # travel times and travel distances
    all_routes = get_all_routes(data, G)

    travel_times = []
    travel_distances = []
    added_edges = []
    unique_distance = 0  # for all vehicles

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
    return travel_times, travel_distances, unique_distance


def get_total_travel_distance(data, G):
    travel_times, travel_distances, unique_distance = distances_and_times(data, G)
    return sum(travel_distances)


def get_total_travel_time(data, G):
    travel_times, travel_distances, unique_distance = distances_and_times(data, G)
    return sum(travel_times)

def get_unique_distance(data, G):
    travel_times, travel_distances, unique_distance = distances_and_times(data, G)
    return unique_distance


def gauss_stopping_rule(delta, p, M, sigma2):
    phi = scipy.stats.norm().cdf(-(M**.5) * delta/(sigma2**.5))
    return (1-p) - 2*phi >= 0


def chebyshev_stopping_rule(delta, p, M, sigma2):
    return (1-p) - sigma2/(M*delta**2) >= 0


def algorithm2(files, path, p, delta, M_0, max_i=None, start_i=0, X_avg=None, X2_avg=None):
    if X_avg is None:
        X_avg = [0]
        X2_avg = [0]

    i = start_i
    while True:
        i += 1
        try:
            data = get_data_from_file(files[i-1])
        except:
            return False, i-1, X_avg, X2_avg, False

        # calculation_time
        # X = get_calculation_time(data)

        G = ox.io.load_graphml(filepath=path / 'map_data.osm')
        # total_travel_distance
        # X = get_total_travel_distance(data, G)

        # total_travel_time
        # X = get_total_travel_time(data, G)

        # unique_distance
        X = get_unique_distance(data, G)

        # coverage
        # total_km = 213.58648499999995 # Favoriten
        # X = get_unique_distance(data, G) / (1000*total_km)


        X_i = ((i-1)/i)*X_avg[-1] + (1/i)*X
        X_avg.append(X_i)

        X2_i = ((i-1)/i)*X2_avg[-1] + (1/i)*X**2
        X2_avg.append(X2_i)

        if i > max_i:
            return False, i-1, X_avg, X2_avg, False
        if i <= M_0:
            continue

        s2 = (i/(i-1))*(X2_i-X_i**2)

        # if gauss_stopping_rule(delta, p, i, s2):
        if chebyshev_stopping_rule(delta, p, i, s2):
            return True, i, X_avg, X2_avg, s2


def main():
    path = Path(__file__).parent.absolute()

    # calculation_time
    # p, delta_abs, M_0 = 0.95, 0.5, 100

    # total_travel_distance
    # p, delta_abs, M_0 = 0.95, 4000, 100

    # total_travel_time
    # p, delta_abs, M_0 = 0.95, 800, 100

    # unique_distance
    p, delta_abs, M_0 = 0.95, 1000, 100

    # coverage
    # p, delta_abs, M_0 = 0.95, 0.005, 100

    max_i = 1000

    files = sorted(path.glob("output/*.json"))
    file_count = len(list(files))
    print(f"file_count: {file_count}\n")

    finished, start_i, X_avg, X2_avg, s2 = algorithm2(files, path, p, delta_abs, M_0, max_i)
    if finished:
        print(finished, start_i, X_avg[-1], X2_avg[-1], s2)
        return

    while start_i < max_i:
        run_simulation_batch()
        files = sorted(path.glob("output/*.json"))
        finished, start_i, X_avg, X2_avg, s2 = algorithm2(
            files, path, p, delta_abs, M_0, max_i, start_i, X_avg, X2_avg)
        if finished:
            print(finished, start_i, X_avg[-1], X2_avg[-1], s2)
            return

    print(finished, start_i, X_avg[-1], X2_avg[-1], s2)

if __name__ == '__main__':
    main()
