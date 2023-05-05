"""
model and vehicle functions
"""

import os
import random
import json
from pprint import pprint

import osmnx as ox


def create_data_model(patrol_locations,
                      time_windows,
                      number_of_vehicles,
                      starts,
                      police_station,
                      time_matrix,
                      osm_to_index):
    """
    puts the time windows, time matrix, number of vehicles, starting
    and end points from the settings file in a usable format for google or-tools
    and returns it as a dictionary called data
    """

    data = {}

    # the police station needs to be index 0
    if police_station != patrol_locations[0]:
        patrol_locations.insert(0, police_station)
        time_windows.insert(0, (0, 86400)) # the vehicles can return any time (whole day = 86400)

    # adding the start locations
    for start in starts:
        if start not in patrol_locations:
            patrol_locations.append(start)
            time_windows.append((0, 0))


    # creates the dictionary to translate the real node numbers to simple ones
    # which can be used by or-tools
    data['osm_to_index'] = {val: key for key, val in enumerate(patrol_locations)}
    data['index_to_osm'] = {val: key for key, val in data['osm_to_index'].items()}

    # indices of all relevant locations in the huge time_matrix
    locations = [osm_to_index[location] for location in patrol_locations]


    # initializes the time matrix for or-tools
    data['time_matrix'] = [[0 for i in patrol_locations] for j in patrol_locations]

    # transfers the important time matrix elements
    for i, row in enumerate(locations):
        for j, column in enumerate(locations):
            data['time_matrix'][i][j] = time_matrix[row][column]

    data['time_windows'] = time_windows
    # data['vehicle_load_time'] = patrolling_time_per_location # already done in config file
    data['num_vehicles'] = number_of_vehicles

    data['police_station'] = data['osm_to_index'][police_station]
    data['starts'] = [data['osm_to_index'][x] for x in starts]
    data['ends'] = [data['police_station'] for x in range(number_of_vehicles)]
    return data


def create_emergencies( number_of_events_min,
                        number_of_events_max,
                        time_of_event_min,
                        time_of_event_max,
                        duration_of_event_min,
                        duration_of_event_max,
                        locations_of_events):
    """creates random interruptions based on the configuration data
     in the settings file"""


    total_number_of_events = random.randint(number_of_events_min, number_of_events_max)

    emergencies = {}
    for emergency_id in range(total_number_of_events):
        emergencies[emergency_id] = {}

        # calculate a start time, duration, location and
        # initialize an end time placeholder
        # a placeholder is needed because the travel time will be added
        emergencies[emergency_id]['start_time']=random.randint(time_of_event_min,
                                                               time_of_event_max)
        emergencies[emergency_id]['duration']=random.randint(duration_of_event_min,
                                                             duration_of_event_max)
        emergencies[emergency_id]['end_time']=None
        emergencies[emergency_id]['location']=random.choice(locations_of_events)
        # alternatively something like random.sample(possibilities, k = 5) could be used

    return emergencies


class Vehicle():
    def __init__(self, v_id, start):
        self.v_id=v_id
        self.emergency_status = False
        self.emergency_ids = []
        self.current_location = start
        self.time_to_curr_location = 0
        self.old_routes = [] # using real nodes
        self.route = [] # using real nodes

    def update_current_route(self, current_time, data, route):
        """
        backups the route and updates it with the new route data
        """
        if current_time > 0:
            self.old_routes.append(self.route.copy())

        # cut the route if not fully driven
        for i, p in enumerate(self.route):
            if p[1] > current_time:
                self.route = self.route[:i]
                break

        self.route += [[data['index_to_osm'][p[0]],
                        current_time+p[1],
                        current_time+p[2]]
                       for p in route]


    def update(self, current_time, time_matrix, osm_to_index):
        """
        calculates current_location and time_to_curr_location
        """

        # calculate current position
        if current_time == 0:
            return
        last_p=self.route[0]

        for p in self.route:
            if p[1] <= current_time <= p[2]:
                self.current_location = p[0]
                self.time_to_curr_location = 0
                break
            elif last_p[2] < current_time < p[1]:
                working_directory = os.path.dirname(__file__) + "/"
                G = ox.io.load_graphml(filepath=working_directory+'map_data.osm')
                route = ox.shortest_path(G, last_p[0], p[0], weight='travel_time')

                travel_time = 0
                for s,e in zip(route[:-1], route[1:]):
                    delta_t = time_matrix[osm_to_index[s]][osm_to_index[e]]
                    travel_time += delta_t

                    t = travel_time+last_p[2]-current_time
                    if t > 0:
                        self.time_to_curr_location = t
                        self.current_location = e

                        break
                break
            last_p = p

        else: # nobreak: current_time > last departure time
            if self.route != []:
                self.current_location = self.route[-1][0]
                self.time_to_curr_location = 0


    def print_vehicle(self):
        """
        just for debugging
        """
        print(self.v_id)
        print(self.emergency_status)
        print(self.emergency_ids)
        print(self.current_location)
        pprint(self.old_routes)
        pprint(self.route)
        print("\n")



def choose_response_vehicle(emergency,
                            vehicles,
                            current_time,
                            time_matrix,
                            osm_to_index,
                            method='random'):
    """
    chooses the vehicle which should report to the emergency
    two methods are available:
    - random
    - fastest: fastest travel time

    uses the current_location and time_to_curr_location properties
    (they should be updated!)

    returns the vehicle id of the response vehicle,
    the arrival time at the emergency and the departure_time after
    the emergency is dealt with
    """

    if method=='random':
        response_vehicle = random.choice([v for v in vehicles if v.emergency_status is False])

        response_v_id = response_vehicle.v_id
        current_location = response_vehicle.current_location
        time_to_curr_location = response_vehicle.time_to_curr_location
        travel_time = time_matrix[osm_to_index[current_location]][osm_to_index[emergency['location']]]

    elif method=='fastest':
        time_data = []
        for v in vehicles:
            if v.emergency_status is True:
                continue

            current_location = v.current_location
            time_to_curr_location = v.time_to_curr_location

            travel_time = time_matrix[osm_to_index[current_location]][osm_to_index[emergency['location']]]
            total_time = time_to_curr_location + travel_time
            time_data.append([total_time, travel_time, time_to_curr_location, v.v_id])

        # choosing the fastest
        total_time, travel_time, time_to_curr_location, response_v_id = min(time_data)

    arrival_time = current_time + time_to_curr_location + travel_time
    departure_time = current_time + time_to_curr_location + travel_time + emergency['duration']

    return response_v_id, arrival_time, departure_time


def update_vpl(visited_patrol_locations, patrol_locations, vehicles, current_time):
    """
    updates the visited patrol locations
    """
    for v in vehicles:
        for p in v.route:
            if p[0] in patrol_locations and p[0] not in visited_patrol_locations:
                if p[1] < current_time:
                    visited_patrol_locations.append(p[0])
    return visited_patrol_locations


def save_to_file(path,
                 seed,
                 vehicles,
                 visited_patrol_locations,
                 emergencies,
                 extra_vehicles):
    """
    creates an output folder and saves the results there as a .json file
    """

    # creating output folder
    if not os.path.exists(f"{path}/output"):
        os.makedirs(f"{path}/output")


    data = dict()
    data['seed']=seed
    vehicles_dict=dict()
    for v in vehicles:
        v_dict=dict()
        v_dict['emergency_ids']=v.emergency_ids
        v_dict['old_routes']=v.old_routes
        v_dict['route']=v.route

        vehicles_dict[v.v_id] = v_dict

    data['vehicles']=vehicles_dict

    data['visited_patrol_locations']=visited_patrol_locations
    data['emergencies']=emergencies
    data['extra_vehicles']=extra_vehicles

    with open(f"{path}/output/{seed}.json", "w") as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == '__main__':
    print("please do not run as main")
