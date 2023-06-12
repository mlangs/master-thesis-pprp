"""
plausibility checks for the results of the simulation
"""
import json
from pathlib import Path

import data_favoriten as d
import config as c


def get_data_from_file(file):
    """
    loads the file data
    """
    with open(file, 'r') as json_file:
        data = json.load(json_file)
    return data



def get_wrong_emergency_length_count(data):
    """
    returns the number of times the emergency duration is not equal to the end-arrival times
    """
    return sum(emergency['duration'] != emergency['end_time']-emergency['arrival_time']
               for emergency in data['emergencies'].values() if emergency['end_time'])



def get_did_not_reach_police_station_count(data, police_station):
    """
    returns the number of times a vehicles is not at the police station
    when the simulation ends
    """
    count = 0
    for vehicle_data in data['vehicles'].values():
        route = vehicle_data['route']
        if route[-1][0] != police_station:
            count += 1
    return count



def get_missed_emergency_mismatch(data):
    """
    returns the number of missed events - number of extra vehicles
    should be 0
    """
    count = sum(emergency['assigned_vehicle_id']
                is None for emergency in data['emergencies'].values())
    return count - len(data['extra_vehicles'])



def get_wrong_travel_time_count(data, time_matrix, osm_to_index):
    """
    returns the number of times a vehicle is faster or slower than it is supposed to
    according to the time matrix
    """
    count = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']
        count += sum(q[1] - p[2] != time_matrix[osm_to_index[p[0]]][osm_to_index[q[0]]]
                     for p, q in zip(route[:-1], route[1:]))
    return count



def get_wrong_time_order_count(data):
    """
    returns the number of times a vehicle leaves before it arrives
    """
    count = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']
        count += sum(p[2] < p[1] for p in route)
    return count



def get_event_wrong_times_count(data):
    """
    returns the number of times the emergency time order is wrong
    """
    count = 0
    for emergency in data['emergencies'].values():
        if emergency['arrival_time'] is None:
            pass
        elif (emergency['arrival_time'] is not None and
              emergency['arrival_time'] < emergency['start_time']):
            count += 1
    return count



def get_random_wait_times_old(data, patrol_locations, police_station):
    """
    returns the time a vehicle spends waiting, when it is not supposed to
    """
    time = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']

        processed_emergency_ids = []  # to subtract the time from the random_leisure_time
        for p in route:
            if p[0] not in patrol_locations + [police_station]:
                for id_e, emergency in data['emergencies'].items():
                    if (int(id_e) in data['vehicles'][v_id]['emergency_ids'] and
                        emergency['location'] == p[0]
                        and emergency['arrival_time'] == p[1]):
                        time -= p[2]-p[1]
                        processed_emergency_ids.append(id_e)

                time += p[2]-p[1]
    return time



def get_random_wait_times(data, patrol_locations, police_station):
    """
    returns the time a vehicle spends waiting, when it is not supposed to
    """
    time = 0
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']

        # add if no patrol_locations or police_station
        time += sum(p[2]-p[1] for p in route if p[0]
                    not in patrol_locations + [police_station])

        # subtract all emergency times if the emergency is not
        # also a patrol location (is was not added either)
        for emergency_id in data['vehicles'][v_id]["emergency_ids"]:
            if data['emergencies'][str(emergency_id)]["location"] not in patrol_locations:
                time -= data['emergencies'][str(emergency_id)]['duration']
    return time



def get_time_at_police_station(data, police_station):
    """
    returns the time spend at the police station
    not useful for testing
    """
    time = []
    for v_id in data['vehicles'].keys():
        route = data['vehicles'][v_id]['route']

        # time spend at the police station
        time.append(sum([p[2]-p[1] for p in route if p[0] == police_station]))
    return time



def get_visited_patrol_locations_duplicate_mismatch(data):
    """
    returns the number of duplicates in the visited_patrol_locations list
    duplicates are not allowed
    """
    return len(data['visited_patrol_locations']) == len(set(data['visited_patrol_locations']))



def get_patrol_locations_mismatch(data, patrol_locations):
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
            if p[0] in patrol_locations and p[2]-p[1] > 0:
                count[p[0]] = count.get(p[0], 0) + 1

    # remove patrol locations a vehicle visited
    for location in data['visited_patrol_locations']:
        count[location] -= 1

    # missing the patrol locations that where visited for patrolling
    # and later for emergencies
    emergency_reference = [[emergency['location'], emergency['arrival_time'],
                            emergency['end_time']] for emergency in data['emergencies'].values()]

    for location in count:
        all_appearances = []
        for v_id in data['vehicles'].keys():
            route = data['vehicles'][v_id]['route']
            for p in route:
                if p[0] in count:
                    all_appearances.append([p[0], p[1], p[2]])

    all_appearances = sorted(all_appearances, key=lambda p: [p[1], p[0]])
    for emergency in emergency_reference:
        location_count = 0
        for location in all_appearances:
            if emergency == location:
                count[location[0]] -= location_count
            elif emergency[0] == location[0]:
                location_count += 1

    # if arrival at the same time to a location
    # which is patrolling and emergency location
    count = {key: val for key, val in count.items() if val != 0}
    for key, val in count.items():
        windows = []
        for p in all_appearances:
            if p[0] == key:
                windows.append([p[1], p[2]])
        for i, window in enumerate(windows[:-1]):
            for window2 in windows[i+1:]:
                if window[1] > window2[0]:
                    count[key] -= 1

    return {key: val for key, val in count.items() if val != 0}



def get_patrolling_times_mismatch(data, police_station, patrolling_time_per_location):
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
            if p[2]-p[1] > 0 and p not in emergency_reference and p[0] != police_station:
                if (p[2]-p[1] != patrolling_time_per_location and
                    route[i+1] not in emergency_reference):
                    if [p[0], p[2]] not in [[x[0], x[2]] for x in emergency_reference]:
                        count += 1
        return count



def get_time_patrolling_mismatch(data, patrolling_time_per_location):
    """
    returns the number of visited_patrol_locations*patrolling_time_per_location - time
    spend patrolling
    should be a positive number in seconds
    the result is the patrolling time lost because the vehicles where send to emergencies
    if the result equals to 0, patrolling was aborted zero times for an emergency
    """
    time = 0
    for vehicle_data in data['vehicles'].values():
        route = vehicle_data['route']

        # add if patrol_locations
        time += sum(p[2]-p[1] for p in route if p[0] in data['visited_patrol_locations'])

        # subtract if emergency location
        for emergency_id in vehicle_data["emergency_ids"]:
            if data['emergencies'][str(emergency_id)]["location"] in data['visited_patrol_locations']:
                time -= data['emergencies'][str(emergency_id)]['duration']

    return len(data['visited_patrol_locations'])*patrolling_time_per_location - time



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
        wrong_emergency_length_count = get_wrong_emergency_length_count(data)
        assert wrong_emergency_length_count == 0

        # number of times a vehicles is not at the police station when the simulation ends
        did_not_reach_police_station_count = get_did_not_reach_police_station_count(
            data, c.POLICE_STATION)
        assert did_not_reach_police_station_count == 0

        # number of missed events - number of extra vehicles (should be 0)
        missed_emergency_mismatch = get_missed_emergency_mismatch(data)
        assert missed_emergency_mismatch == 0

        # travel times need to match those in d.time_matrix
        wrong_travel_time_count = get_wrong_travel_time_count(data, d.time_matrix, d.osm_to_index)
        assert wrong_travel_time_count == 0

        # number of times the depature is earlier than the arrival
        wrong_time_order_count = get_wrong_time_order_count(data)
        assert wrong_time_order_count == 0

        # number of times the emergency time order is wrong
        event_wrong_times_count = get_event_wrong_times_count(data)
        assert event_wrong_times_count == 0

        # old version
        # time a vehicle spends waiting, when it is not supposed to
        random_wait_times_old = get_random_wait_times_old(
            data, c.PATROL_LOCATIONS, c.POLICE_STATION)
        assert random_wait_times_old == 0

        # time a vehicle spends waiting, when it is not supposed to
        random_wait_times = get_random_wait_times(data, c.PATROL_LOCATIONS, c.POLICE_STATION)
        assert random_wait_times == 0

        # time spend at the police station
        # no test, just information
        time_at_police_station = get_time_at_police_station(data, c.POLICE_STATION)
        # print(time_at_police_station)
        assert all(t >= 0 for t in time_at_police_station)

        # number of duplicates in the visited_patrol_locations list
        no_duplicates = get_visited_patrol_locations_duplicate_mismatch(data)
        assert no_duplicates

        # count of not plausible stays
        patrol_locations_mismatch = get_patrol_locations_mismatch(
            data, c.PATROL_LOCATIONS)
        assert not patrol_locations_mismatch

        # number of times the patrolling time is not the patrolling_time_per_location
        # and the vehicle is not called to an emergency and has to abort patrolling
        patrolling_times_mismatch = get_patrolling_times_mismatch(
            data, c.POLICE_STATION, c.PATROLLING_TIME_PER_LOCATION)
        assert patrolling_times_mismatch == 0

        # number of visited_patrol_locations*patrolling_time_per_location - time
        # spend patrolling
        # result is the patrolling time lost because the vehicles where send to emergencies
        time_patrolling_mismatch = get_time_patrolling_mismatch(
            data, c.PATROLLING_TIME_PER_LOCATION)
        assert time_patrolling_mismatch >= 0



if __name__ == '__main__':
    main()
