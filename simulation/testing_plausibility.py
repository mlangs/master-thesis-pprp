"""
plausibility checks for the results of the simulation
"""
import json
from pathlib import Path

import data_favoriten as d


def get_data_from_file(file):
    """
    loads the file data and returns it as dictionary
    """
    with open(file, 'r') as json_file:
        data = json.load(json_file)
    return data



def get_emergency_length_errors(data):
    """
    returns the number of times the emergency duration is not equal to the end-arrival times
    """
    return sum(emergency['duration'] != emergency['end_time']-emergency['arrival_time']
               for emergency in data['emergencies'].values() if emergency['end_time'])



def get_emergency_time_errors(data):
    """
    returns the number of times the emergency time order is wrong
    """
    count = 0
    for emergency in data['emergencies'].values():
        if emergency['arrival_time'] is None:
            pass
        elif emergency['arrival_time'] < emergency['start_time']:
            count += 1
    return count



def get_missed_emergencies_errors(data):
    """
    returns the number of missed events - number of extra vehicles
    should be 0
    """
    count_missed_emergencies = sum(emergency['assigned_vehicle_id']
                is None for emergency in data['emergencies'].values())
    count_extra_vehicles = len(data['extra_vehicles'])
    return count_missed_emergencies - count_extra_vehicles



def get_did_not_reach_police_station_errors(data):
    """
    returns the number of times a vehicles is not at the police station
    when the simulation ends
    """
    count = 0
    for vehicle_data in data['vehicles'].values():
        route = vehicle_data['route']
        if route[-1][0] != data['police_station']:
            count += 1
    return count


def get_travel_time_errors(data, time_matrix, osm_to_index):
    """
    returns the number of times a vehicle is faster or slower than it is supposed to
    according to the time matrix
    """
    count = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']
        for p, q in zip(route[:-1], route[1:]):
            if q[1] - p[2] != time_matrix[osm_to_index[p[0]]][osm_to_index[q[0]]]:
                # print(v_id, q, p, time_matrix[osm_to_index[p[0]]][osm_to_index[q[0]]])
                count += 1
    return count



def get_time_order_errors(data):
    """
    returns the number of times a vehicle leaves before it arrives
    """
    count = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']
        count += sum(p[2] < p[1] for p in route)
    return count



def get_wait_times_at_wrong_locations(data):
    """
    returns the difference between the
    time a vehicle spends waiting at a location other
    than a patrol location or the police station and
    attended emergencies accumulated at locations which are not
    patrol locations or the police station
    """
    patrol_and_police_locations = data['patrol_locations'] + [data['police_station']]

    time = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']

        # add if no patrol_locations or police_station
        time += sum(p[2]-p[1] for p in route if p[0] not in patrol_and_police_locations)

        # subtract all emergency times if the emergency is not
        # also a patrol location (is was not added either)
        for emergency_id in data['vehicles'][v_id]["emergency_ids"]:
            if data['emergencies'][str(emergency_id)]["location"] not in patrol_and_police_locations:
                time -= data['emergencies'][str(emergency_id)]['duration']
    return time



def get_visited_locations_duplicate_mismatch(data):
    """
    returns true if there are no duplicates in the visited_locations list
    duplicates are not allowed
    """
    return len(data['visited_locations']) == len(set(data['visited_locations']))



def get_not_plausible_patrol_locations_visits(data):
    """
    adding all visits at patrol locations with p[2]-p[1] > 0 to a dictionary
    and removing all visited locations and emergencies again
    --> should return empty dictionary
    """
    count = {}
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']

        # counts all visits at patrol locations withs p[2]-p[1] > 0
        for p in route:
            if p[0] in data['patrol_locations'] and p[2]-p[1] > 0:
                count[p[0]] = count.get(p[0], 0) - 1

    # remove patrol locations a vehicle visited
    for location in data['visited_locations']:
        count[location] = count.get(location, 0) + 1

    # removing emergency locations
    for emergency in data['emergencies'].values():
        if emergency['location'] in data['patrol_locations'] and emergency['arrival_time']:
            count[emergency['location']] += 1

    # count < 0 possible because sometimes a patrol location is only visited for emergencies
    return {key: val for key, val in count.items() if val < 0}



def get_patrolling_time_errors(data):
    """
    returns the number of times the patrolling time is not the patrolling_time_per_location
    and the vehicle is not called to an emergency and has to abort patrolling
    """
    emergency_reference = [[emergency['location'], emergency['arrival_time'],
                            emergency['end_time']] for emergency in data['emergencies'].values()]

    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']
        count = 0
        for i, p in enumerate(route[:-1]):
            # continue in following cases
            if (# staying at the police station
                p[0] == data['police_station']
                # just passing the location
                or p[2]-p[1] == 0
                # patrolling at the location
                or (p[2]-p[1] == data['patrolling_time_per_location'] and p[0] in data['patrol_locations'])
                # staying at the patrol location, but leaving for an emergency
                or (p[0] in data['patrol_locations'] and route[i+1] in emergency_reference)
                # staying because of an emergency
                or p in emergency_reference
                # staying longer because an emergency appeared at the location
                or (p[0] in data['patrol_locations'] and [p[0], p[2]] in [[x[0], x[2]] for x in emergency_reference])):
                continue
            count += 1
    return count



def main():
    """
    plausibility checks for the results of the simulation
    """
    path = Path(__file__).parent.absolute()
    files = path.glob("output/*.json")

    file_count = len(list(files))
    print(f"file_count: {file_count}\n")

    for file in path.glob("output/*.json"):
        data = get_data_from_file(file)

        # number of times the emergency duration is not equal to the end-arrival times
        emergency_length_errors = get_emergency_length_errors(data)
        assert emergency_length_errors == 0

        # number of times the emergency time order is wrong
        emergency_time_errors = get_emergency_time_errors(data)
        assert emergency_time_errors == 0

        # number of missed events == number of extra vehicles (should be 0)
        missed_emergency_errors = get_missed_emergencies_errors(data)
        assert missed_emergency_errors == 0

        # number of times a vehicles is not at the police station when the simulation ends
        did_not_reach_police_station_errors = get_did_not_reach_police_station_errors(data)
        assert did_not_reach_police_station_errors == 0

        # travel times need to match those in d.time_matrix
        travel_time_errors = get_travel_time_errors(data, d.time_matrix, d.osm_to_index)
        assert travel_time_errors == 0

        # number of times the depature is earlier than the arrival
        time_order_errors = get_time_order_errors(data)
        assert time_order_errors == 0

        # time a vehicle spends waiting, where it is not supposed to
        wait_times_at_wrong_locations = get_wait_times_at_wrong_locations(data)
        assert wait_times_at_wrong_locations == 0

        # number of duplicates in the visited_locations list
        no_duplicates = get_visited_locations_duplicate_mismatch(data)
        assert no_duplicates

        # count of not plausible stays
        not_plausible_patrol_locations = get_not_plausible_patrol_locations_visits(data)
        assert not not_plausible_patrol_locations

        # returns the number of times the the duration of a stay is not correct
        patrolling_time_errors = get_patrolling_time_errors(data)
        assert patrolling_time_errors == 0



if __name__ == '__main__':
    main()
