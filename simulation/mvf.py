"""
model and vehicle functions
"""

import random
import json
from pprint import pprint

import osmnx as ox


def create_emergencies(number_of_events_mu,
                       number_of_events_sigma,
                       time_of_event_min,
                       time_of_event_max,
                       event_duration_mu,
                       event_duration_sigma,
                       locations_of_events):
    """
    creates random interruptions using normal distributed random numbers
    based on the configuration data in the settings file
    """

    total_number_of_events = -1
    while total_number_of_events < 0:
        total_number_of_events = round(random.gauss(mu=number_of_events_mu,
                                                    sigma=number_of_events_sigma))

    emergencies = {}
    for emergency_id in range(total_number_of_events):
        emergencies[emergency_id] = {}

        # calculate a start time, duration, location and
        # initialize an end_time placeholder
        # a placeholder is needed because the travel time will be added
        emergencies[emergency_id]['start_time']=random.randint(time_of_event_min,
                                                               time_of_event_max)

        event_duration = -1
        while event_duration < 0:
            event_duration = round(random.gauss(mu=event_duration_mu,
                                                sigma=event_duration_sigma))
        emergencies[emergency_id]['duration'] = event_duration
        emergencies[emergency_id]['arrival_time']=None
        emergencies[emergency_id]['end_time']=None
        emergencies[emergency_id]['assigned_vehicle_id']=None
        # drawing a location for each events allows duplicates
        emergencies[emergency_id]['location']=random.choice(locations_of_events)

    return emergencies



def update_locations_and_windows(patrol_locations,
                                 time_windows,
                                 vehicles,
                                 police_station,
                                 patrolling_time_per_location):
    """
    prepares the locations and time windows for the create_data_model function
    time windows need to get handled differently for different cases
    to force the correct behavior
    """

    updated_patrol_locations = patrol_locations.copy()
    dummy_locations = []

    # the police station needs to be index 0 and cannot be a patrol_location
    if police_station not in updated_patrol_locations:
        updated_patrol_locations.insert(0, police_station)
        time_windows.insert(0, (0, 86400)) # the vehicles can return any time (whole day = 86400)

    starts = []

    # adding and adapting the start locations
    for v in vehicles:
        if v.emergency_status is True:
            continue

        start = v.current_location
        starts.append(start)
        arrival_time = v.time_to_curr_location

        if start not in updated_patrol_locations: # not patrol location and not police station
            dummy_locations.append([len(updated_patrol_locations), start])
            updated_patrol_locations.append(start)
            time_windows.append((arrival_time, arrival_time))

        elif start == police_station: # police station
            dummy_locations.append([len(updated_patrol_locations), start])
            updated_patrol_locations.append(start)
            time_windows.append((arrival_time, 86400))

        elif start not in patrol_locations: # arbitrary other start
            if starts.count(start) > 1: # duplicated start
                dummy_locations.append([len(updated_patrol_locations), start])
            updated_patrol_locations.append(start)
            #departure_time = 86400 if start == police_station else arrival_time
            time_windows.append((arrival_time, arrival_time))

        elif start in patrol_locations: # currently at patrol location
            # looking at vehicles that start at the current location
            all_ids_with_start = [v.v_id for v in vehicles if v.current_location == start]
            # sorting the vehicles according to arrival
            # (so the patrolling vehicle continues patrolling)
            all_ids_with_start = sorted(all_ids_with_start,
                                        key=lambda idx: [-vehicles[idx].time_at_curr_location,
                                                         vehicles[idx].time_to_curr_location])

            # first appearance
            if starts.count(start) == 1:
                idx = updated_patrol_locations.index(start)
                # if patrolling: adjusting time window accordingly
                if all_ids_with_start.index(v.v_id) == 0:
                    window = (arrival_time+patrolling_time_per_location-v.time_at_curr_location,
                              arrival_time+patrolling_time_per_location-v.time_at_curr_location)
                # not patrolling
                else:

                    window = (arrival_time, arrival_time)
                time_windows[idx] = window

            # duplicated start from patrol location
            else:
                dummy_locations.append([len(updated_patrol_locations), start])
                updated_patrol_locations.append(start)
                # if patrolling: adjusting time window accordingly
                if all_ids_with_start.index(v.v_id) == 0:
                    window = (arrival_time+patrolling_time_per_location-v.time_at_curr_location,
                              arrival_time+patrolling_time_per_location-v.time_at_curr_location)
                # not patrolling
                else:
                    window = (arrival_time, arrival_time)
                time_windows.append(window)

    return starts, dummy_locations, updated_patrol_locations, time_windows



def create_data_model(patrol_locations,
                      updated_patrol_locations,
                      time_windows,
                      starts,
                      dummy_locations,
                      police_station,
                      time_matrix,
                      osm_to_index):
    """
    creates the data dictionary, which is needed for ortools
    """

    data = {}

    # creates the dictionary to translate the real node numbers to simple ones
    # which can be used by ortools
    data['osm_to_index'] = {val: key for key, val in enumerate([police_station]+patrol_locations)}
    data['index_to_osm'] = {val:key for key, val in data['osm_to_index'].items()}
    data['index_to_osm'].update(dummy_locations)

    # indices of all relevant locations in the huge time_matrix
    locations = [osm_to_index[location] for location in updated_patrol_locations]

    # initializes the time matrix for ortools
    data['time_matrix'] = [[0 for i in updated_patrol_locations] for j in updated_patrol_locations]

    # transfers the important time matrix elements
    for i, row in enumerate(locations):
        for j, column in enumerate(locations):
            data['time_matrix'][i][j] = time_matrix[row][column]

    data['time_windows'] = time_windows
    # data['vehicle_load_time'] = patrolling_time_per_location # already done in config file
    data['num_vehicles'] = len(starts)
    data['police_station'] = data['osm_to_index'][police_station]

    data['starts'] = []
    for start in starts:
        if ((start != police_station) and
            (start in data['osm_to_index']) and
            (data['osm_to_index'][start] not in data['starts'])):
            data['starts'].append(data['osm_to_index'][start])
        else:
            dummy_start = dummy_locations.pop(0)
            idx = dummy_start[0]
            data['starts'].append(idx)

    data['ends'] = [data['police_station'] for _ in range(data['num_vehicles'])]
    return data



def update_patrol_locations_and_time_windows(patrol_locations,
                                             time_windows,
                                             visited_locations,
                                             current_time):
    """
    removes visited patrol locations, removes patrol locations with
    missed time windows and adapts time windows
    """

    new_patrol_locations = []
    new_time_windows = []
    for patrol_location, time_window in zip(patrol_locations, time_windows):
        if ( patrol_location in visited_locations or
                time_window[1]-current_time <= 0 ): # departure time cannot be negative
            continue
        else:
            new_patrol_locations.append(patrol_location)
            new_time_windows.append( (max(0, time_window[0]-current_time),
                                        time_window[1]-current_time) )

    return new_patrol_locations, new_time_windows



class Vehicle():
    """
    Vehicle class to update vehicles and to keep track of vehicle information
    """
    def __init__(self, v_id, start):
        self.v_id=v_id
        self.emergency_status = False
        self.emergency_ids = []
        self.current_location = start
        self.time_to_curr_location = 0
        self.time_at_curr_location = 0
        self.old_routes = [] # using real nodes
        self.route = [] # using real nodes


    def update(self, current_time, time_matrix, osm_to_index, path):
        """
        calculates current_location, time_to_curr_location, time_at_curr_location
        """

        # if current_time is 0, there is nothing to do
        if current_time == 0:
            return

        last=self.route[0]
        for location, arrival, departure in self.route:

            # if in a time interval at a location, use the location
            if arrival <= current_time <= departure:
                self.current_location = location
                self.time_to_curr_location = 0
                self.time_at_curr_location = current_time-arrival
                break

            # if not in a time interval at a location, calculate the current position
            # by calculation the route from the last point to the next point
            # and see where the vehicle should be right now
            elif last[2] < current_time < arrival:
                G = ox.io.load_graphml(filepath=path / 'map_data.osm')
                route = ox.shortest_path(G, last[0], location, weight='travel_time')

                travel_time = 0
                for s,e in zip(route[:-1], route[1:]):
                    delta_t = time_matrix[osm_to_index[s]][osm_to_index[e]]
                    travel_time += delta_t

                    # t = travel_time+last[2]-current_time
                    t = current_time-last[2]-travel_time
                    if t < 0:
                        self.time_to_curr_location = -t
                        self.current_location = e
                        self.time_at_curr_location = 0
                        break
                break
            last = [location, arrival, departure]

        else: # nobreak: current_time > last departure time
            if self.route != []:
                self.current_location = self.route[-1][0]
                self.time_to_curr_location = 0
                self.time_at_curr_location = current_time-self.route[-1][2]


    def update_current_route(self, current_time, data, route):
        """
        does a backup of the route and updates it with the new route data
        """
        def clean_route(route):
            cleaned_route = []
            for p in route:
                if not cleaned_route:
                    cleaned_route.append(p)
                elif cleaned_route[-1][0] == p[0]:
                    cleaned_route[-1] = [cleaned_route[-1][0], cleaned_route[-1][1], p[2]]
                else:
                    cleaned_route.append(p)
            return cleaned_route

        if current_time > 0:
            self.old_routes.append(self.route.copy())

        # cut the route if not fully driven
        for i, p in enumerate(self.route):
            if p[1] <= current_time <= p[2]:
                self.route[i][2] = current_time
            if p[1] > current_time:
                self.route = self.route[:i]
                break

        # adding the new time windows adjusted to global time
        # the max statement is needed because ortools thinks
        # the vehicle is waiting at the location
        self.route += [[data['index_to_osm'][p[0]],
                        current_time+max(p[1], self.time_to_curr_location),
                        current_time+p[2]]
                       for p in route]

        self.route = clean_route(self.route)


    def print_vehicle(self):
        """
        used only for debugging
        """
        print(self.v_id)
        print(self.emergency_status)
        print(self.emergency_ids)
        print(self.current_location)
        print(self.time_to_curr_location)
        print(self.time_at_curr_location)
        pprint(self.old_routes)
        pprint(self.route)
        print("\n")



def choose_response_vehicle(emergency,
                            vehicles,
                            current_time,
                            time_matrix,
                            osm_to_index,
                            method='fastest'):
    """
    chooses the vehicle which should report to the emergency
    two methods are available:
    - random
    - fastest: fastest travel_time

    uses the current_location and time_to_curr_location properties
    (they need to be updated first!)

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

        # collecting the reaction time for all available vehicles
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



def update_vl(visited_locations, patrol_locations, vehicles, current_time):
    """
    updates the visited locations list
    a patrol location is considered "visited" if some time
    was spend there (also if the time was during an emergency)
    """
    for v in vehicles:
        for p in v.route:
            if p[0] not in patrol_locations:
                continue
            if p[0] in visited_locations:
                continue

            if p[1] < p[2] and p[2] <= current_time:
                visited_locations.append(p[0])

    return visited_locations



def save_to_file(path,
                 firstsolutionstategy,
                 localsearchmetaheuristic,
                 solution_limit,
                 time_limit,
                 patrol_locations,
                 police_station,
                 patrolling_time_per_location,
                 seed,
                 vehicles,
                 visited_locations,
                 emergencies,
                 extra_vehicles,
                 calculation_time):
    """
    creates an output folder and saves the results there as a .json file
    """

    # creating output folder
    output_directory = path / 'output'
    output_directory.mkdir(exist_ok=True)

    data = {}
    data['seed']=seed
    data['calculation_time']=calculation_time
    data['firstsolutionstategy'] = firstsolutionstategy
    data['localsearchmetaheuristic'] = localsearchmetaheuristic
    data['solution_limit'] = solution_limit
    data['time_limit'] = time_limit
    data['patrol_locations'] = patrol_locations
    data['police_station'] = police_station
    data['patrolling_time_per_location'] = patrolling_time_per_location

    vehicles_dict={}
    for v in vehicles:
        v_dict={}
        v_dict['emergency_ids']=v.emergency_ids
        v_dict['old_routes']=v.old_routes
        v_dict['route']=v.route

        vehicles_dict[v.v_id] = v_dict

    data['vehicles']=vehicles_dict

    data['visited_locations']=visited_locations
    data['emergencies']=emergencies
    data['extra_vehicles']=extra_vehicles

    output_file = output_directory / f"{seed}.json"
    with output_file.open(mode="w") as outfile:
        json.dump(data, outfile, indent=4)



if __name__ == '__main__':
    print("please do not run as main")
