"""
saving images of the routes which can be converted to a gif
"""

import json
from pathlib import Path

import osmnx as ox
import matplotlib.pyplot as plt

import data_favoriten as d
import config as c



def get_data(file):
    """
    getting the simulation data
    """
    with open(file, 'r') as json_file:
        data = json.load(json_file)
    return data



def get_all_routes(data, G):
    """
    getting all routes with extra steps
    """
    all_routes = []
    for v_id in data['vehicles']:
        route = data['vehicles'][v_id]['route']
        complete_route = []

        complete_route.append(route[0])
        for start, end in zip(route[:-1], route[1:]):
            # route = ox.shortest_path(G, ORIGIN_NODE, DESTINATION_NODE, weight='travel_time')
            partial_route = ox.shortest_path(G, start[0], end[0], weight='travel_time')

            for i, location in enumerate(partial_route[1:-1]):
                arrival_time = complete_route[-1][2] + \
                    d.time_matrix[d.osm_to_index[location]][d.osm_to_index[partial_route[1:][i+1]]]
                complete_route.append([location, arrival_time, arrival_time])
            complete_route.append(end)

        all_routes.append(complete_route)
    return all_routes



def get_emergency_location_times(data):
    """
    collecting all emergency locations with their start, arrival and end times
    """
    emergency_location_times = []
    for emergency in data['emergencies'].values():
        emergency_location_times. append([emergency['location'],
                                          emergency['start_time'],
                                          emergency['arrival_time'],
                                          emergency['end_time']])
    return emergency_location_times



def main():
    """
    generating and saving images
    """
    path = Path(__file__).parent.absolute()
    seed = 1686670141043741808
    
    data = get_data(path / f"output/{seed}.json")
    G = ox.io.load_graphml(filepath=path / 'map_data.osm')

    # preparing emergency data and routes
    emergency_location_times = get_emergency_location_times(data)
    all_routes = get_all_routes(data, G)

    time_step = 60
    times = list(range(0, 60*60*3, time_step))

    for time in times:
        fig, ax = ox.plot_graph(G, bgcolor='#999999', node_color='k',
                                edge_color='k', show=False, close=False)

        # setting the title
        ax.set_title(f"{time//60+1} min")

        # plotting the police station
        x = G.nodes()[c.POLICE_STATION]["x"]
        y = G.nodes()[c.POLICE_STATION]["y"]
        ax.scatter(x, y, c='w', s=17)

        # plotting the patrolling locations
        for location in c.PATROL_LOCATIONS:
            x = G.nodes()[location]["x"]
            y = G.nodes()[location]["y"]
            ax.scatter(x, y, c='cyan', s=12)

        # plotting emergency nodes
        for emergency in emergency_location_times:
            x = G.nodes()[emergency[0]]["x"]
            y = G.nodes()[emergency[0]]["y"]

            if time < emergency[1]:
                pass
            elif emergency[2] is None:
                ax.scatter(x, y, c='magenta', s=12)
            elif time < emergency[2]:
                ax.scatter(x, y, c='red', s=12)
            elif time < emergency[3]:
                ax.scatter(x, y, c='orange', s=12)
            else:
                ax.scatter(x, y, c='lightgray', s=12)

        # plotting the routes
        routes = []
        for v_id in data['vehicles']:
            route = [p for p in all_routes[int(v_id)] if p[1] <= time]
            route.insert(0, all_routes[int(v_id)][0])
            routes.append(route)

        for i, route in enumerate(routes):
            for node in route:
                x_values = [G.nodes()[node[0]]["x"] for node in route]
                y_values = [G.nodes()[node[0]]["y"] for node in route]

                ax.plot(x_values, y_values,
                        color=['dodgerblue',
                               'steelblue',
                               'deepskyblue',
                               'powderblue',
                               'cadetblue'][i],
                        linestyle='-', linewidth=1)

                # plotting visited patrol locations
                if node[2]-node[1] > 0 and node[0] in c.PATROL_LOCATIONS:
                    x = G.nodes()[node[0]]["x"]
                    y = G.nodes()[node[0]]["y"]
                    ax.scatter(x, y, c='b', s=12)

        plt.savefig(path / f"img/gif_{str(time//60+1).zfill(4)}.jpg",  dpi=100)
        plt.close()



if __name__ == '__main__':
    main()
