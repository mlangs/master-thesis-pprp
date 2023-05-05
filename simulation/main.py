"""main file for running the simulation"""

import os
import time
import random
import concurrent.futures # used for multi-processing

import config as c # the settings file
import data_favoriten as d # processed map data
import mvf # "function module"
import vrptw_metaheuristic as vm # or-tools functions


def run_simulation():
    # seed = time.time # returns a float (supported in random.seed)
    seed = time.time_ns() # returns an integer (nanoseconds)
    random.seed(seed)

    print(f"\nStarting simulation with seed: {seed}")

    # simulation time in seconds
    current_time = 0

    # initialise vehicles
    vehicles = [mvf.Vehicle(v_id=i, start=c.starts[i])
                for i in range(c.number_of_vehicles)]

    # for keeping track of a lack of vehicles
    # for example: all vehicles are at emergencies and another emergency occurs
    extra_vehicles = []

    # for keeping track of visited patrol locations
    visited_patrol_locations = []

    # create a list of emergencies
    emergencies = mvf.create_emergencies(c.number_of_events_min,
                                         c.number_of_events_max,
                                         c.time_of_event_min,
                                         c.time_of_event_max,
                                         c.duration_of_event_min,
                                         c.duration_of_event_max,
                                         c.possible_locations_of_events)

    # initialize a event queue
    event_queue = [{'event_id': i,
                    'type': 'start',
                    'time': emergencies[i]['start_time']} for i in emergencies]


    # loop through the event queue
    while True:
        # sort events by time (and id if two events start at the same time)
        event_queue = sorted(event_queue, key=lambda x: (x['time'], x['event_id']))

        # define new vehicle starting positions for available vehicles
        # vehicle objects are updated after a new event pops
        starts = [v.current_location for v in vehicles if v.emergency_status is False]
        number_of_vehicles = len(starts)

        # remove already visited patrol locations and
        # reduce time windows (if time has passed)
        patrol_locations = []
        time_windows = []
        for patrol_location, time_window in zip(c.patrol_locations, c.time_windows):
            if ( patrol_location in visited_patrol_locations or
                    time_window[1]-current_time <= 0 ): # departure time cannot be negative
                continue
            else:
                patrol_locations.append(patrol_location)
                time_windows.append( (max(0, time_window[0]-current_time),
                                     time_window[1]-current_time) )


        # if there are no patrol locations left to process
        # the route back to the police station is calculated
        # for all vehicles which currently handle an emergency
        # and the while loop is exited
        if not patrol_locations:
            for v in vehicles:
                if v.route[-1][0] != c.police_station:
                    travel_time = d.time_matrix[d.osm_to_index[v.current_location]][d.osm_to_index[c.police_station]]
                    arrival_time = v.route[-1][2]+travel_time
                    v.route.append([c.police_station, arrival_time, arrival_time])
            break

        # if cars are available, new routes can be calculated
        if any([v.emergency_status is False for v in vehicles]):
            # get data dictionary usable by or-tools
            data = mvf.create_data_model(patrol_locations,
                                        time_windows,
                                        number_of_vehicles,
                                        starts,
                                        c.police_station,
                                        d.time_matrix,
                                        d.osm_to_index)

            # calculating the routes
            planned_routes = vm.plan_routes(data,
                                            c.max_patrolling_time_per_vehicle,
                                            c.patrolling_time_per_location)

            # update vehicle objects with the new routes
            for v, route in zip( [v for v in vehicles if v.emergency_status is False],
                                planned_routes.values() ):
                v.update_current_route(current_time, data, route)


        # exit the while loop if no more events are available to handle
        if not event_queue:
            break


        # process next event and adjust the current time accordingly
        current_event = event_queue.pop(0)
        current_time = current_event['time']

        # update the position of all vehicles
        for v in vehicles:
            v.update(current_time, d.time_matrix, d.osm_to_index)

        # update visited patrol locations
        visited_patrol_locations = mvf.update_vpl(visited_patrol_locations,
                                                  c.patrol_locations,
                                                  vehicles,
                                                  current_time)

        # handle the event
        if current_event['type'] == 'end':
            v_id = current_event['assigned']
            vehicles[v_id].emergency_status = False

        elif current_event['type'] == 'start':
            location = emergencies[current_event['event_id']]['location']

            # if there is no vehicle available an extra vehicle needs to take over
            # no new route needs to be calculated
            if all([v.emergency_status for v in vehicles]):
                extra_vehicles.append(emergencies[current_event['event_id']])
                continue

            # find response vehicle and calculate when the vehicle will be available again
            v_id, arrival_time, return_time = mvf.choose_response_vehicle(
                                                    emergencies[current_event['event_id']],
                                                    vehicles,
                                                    current_time,
                                                    d.time_matrix,
                                                    d.osm_to_index,
                                                    method='fastest')

            # keep track of the emergency and set the status
            vehicles[v_id].emergency_status = True
            vehicles[v_id].emergency_ids.append([current_event['event_id'], arrival_time])

            # adjusting the route and appending the new arrival location
            vehicles[v_id].update_current_route(current_time, data, [])
            vehicles[v_id].route.append([location, arrival_time, return_time])

            # adding the event for the end of the emergency to the event queue
            # (events will be sorted at the start of every loop)
            event_queue.append({'event_id': current_event['event_id'],
                                'type': 'end',
                                'time': return_time,
                                'assigned': v_id})




    # updating the visited patrol locations
    visited_patrol_locations = mvf.update_vpl(visited_patrol_locations,
                                              c.patrol_locations,
                                              vehicles,
                                              current_time)


    # save seed, vehicle data (including routes), visited patrol locations, emergencies
    # and demand of extra vehicles to a json file
    path = os.path.dirname(os.path.abspath(__file__))
    mvf.save_to_file(path,
                     seed,
                     vehicles,
                     visited_patrol_locations,
                     emergencies,
                     extra_vehicles)
    return f"Seed {seed} done."



def main(number_of_simulations):
    """
    runs the simulate function
    uses multiprocessing
    """

    start = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        results = [executor.submit(run_simulation) for _ in range(number_of_simulations)]

        for future in concurrent.futures.as_completed(results):
            print(f"COMPLETED: {future.result()}")
    end = time.perf_counter()
    print(f'Concurrent: Finished in {round(end-start, 2)} second(s)')



if __name__ == "__main__":
    NUMBER_OF_SIMULATIONS = 1
    main(NUMBER_OF_SIMULATIONS)
