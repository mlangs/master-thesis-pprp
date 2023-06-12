"""main file for running the simulation"""

import time
import random
import concurrent.futures # used for multi-processing

import config as c # the settings file
import data_favoriten as d # processed map data
import mvf # "function module"
import vrptw_metaheuristic as vm # ortools functions


def run_simulation():
    """
    runs the simulation one time
    """
    simulation_start_time = time.perf_counter() # pref_counter_ns

    # seed = time.time # returns a float (supported in random.seed)
    seed = time.time_ns() # returns an integer (nanoseconds)
    random.seed(seed)

    print(f"\nStarting simulation with seed: {seed}")

    # simulation time in seconds
    current_time = 0

    # initialise vehicles
    vehicles = [mvf.Vehicle(v_id=i, start=c.STARTS[i])
                for i in range(c.NUMBER_OF_VEHICLES)]

    # for keeping track of a lack of vehicles
    # for example: all vehicles are at emergencies and another emergency occurs
    extra_vehicles = {}

    # for keeping track of visited patrol locations
    visited_patrol_locations = []

    # create a list of emergencies
    emergencies = mvf.create_emergencies(c.NUMBER_OF_EVENTS_MU,
                                         c.NUMBER_OF_EVENTS_SIGMA,
                                         c.TIME_OF_EVENT_MIN,
                                         c.TIME_OF_EVENT_MAX,
                                         c.EVENT_DURATION_MU,
                                         c.EVENT_DURATION_SIGMA,
                                         c.POSSIBLE_LOCATIONS_OF_EVENTS)
    # initialize a event queue
    event_queue = [{'event_id': i,
                    'type': 'start',
                    'time': emergency['start_time']} for i, emergency in emergencies.items()]


    # loop through the event queue
    while True:
        # sort events by time (and id if two events start at the same time)
        event_queue = sorted(event_queue, key=lambda x: (x['time'], x['event_id']))

        # remove visited patrol locations and patrol locations with
        # missed time windows
        # adapt time windows
        patrol_locations, time_windows = mvf.update_patrol_locations_and_time_windows(
                                                c.PATROL_LOCATIONS,
                                                c.TIME_WINDOWS,
                                                visited_patrol_locations,
                                                current_time)


        # if there are no patrol locations left to process
        # the route back to the police station is calculated
        # for all vehicles which currently handle an emergency
        # and the while loop is exited
        #if not patrol_locations:
        #    for v in vehicles:
        #        if v.route[-1][0] != c.POLICE_STATION:
        #            travel_time = d.time_matrix[d.osm_to_index[v.current_location]][d.osm_to_index[c.POLICE_STATION]]
        #            arrival_time = v.route[-1][2]+travel_time+v.time_to_curr_location
        #            v.route.append([c.POLICE_STATION, arrival_time, arrival_time])
        #    break

        # if cars are available, new routes can be calculated
        if any([v.emergency_status is False for v in vehicles]):
            locations_and_windows = mvf.update_locations_and_windows(patrol_locations,
                                                                     time_windows,
                                                                     vehicles,
                                                                     c.POLICE_STATION,
                                                                     c.PATROLLING_TIME_PER_LOCATION)

            starts, dummy_locations, updated_patrol_locations, time_windows = locations_and_windows


            # get data dictionary usable by ortools
            data = mvf.create_data_model(patrol_locations,
                                         updated_patrol_locations,
                                         time_windows,
                                         starts,
                                         dummy_locations,
                                         c.POLICE_STATION,
                                         d.time_matrix,
                                         d.osm_to_index)

            # calculating the routes
            planned_routes = vm.plan_routes(data,
                                            c.MAX_PATROLLING_TIME_PER_VEHICLE,
                                            c.PATROLLING_TIME_PER_LOCATION)

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
            v.update(current_time, d.time_matrix, d.osm_to_index, c.path)

        # update visited patrol locations
        visited_patrol_locations = mvf.update_vpl(visited_patrol_locations,
                                                  c.PATROL_LOCATIONS,
                                                  vehicles,
                                                  current_time)

        # handle the event
        if current_event['type'] == 'end':
            v_id = current_event['assigned']
            vehicles[v_id].emergency_status = False

        elif current_event['type'] == 'start':
            emergency_id = current_event['event_id']

            location = emergencies[emergency_id]['location']

            # if there is no vehicle available an extra vehicle needs to take over
            # no new route needs to be calculated
            if all([v.emergency_status for v in vehicles]):
                extra_vehicles[emergency_id] = emergencies[emergency_id]
                continue

            # find response vehicle and calculate when the vehicle will be available again
            v_id, arrival_time, return_time = mvf.choose_response_vehicle(
                                                    emergencies[emergency_id],
                                                    vehicles,
                                                    current_time,
                                                    d.time_matrix,
                                                    d.osm_to_index,
                                                    method='fastest')

            # add infos to emergencies
            emergencies[emergency_id]['arrival_time'] = arrival_time
            emergencies[emergency_id]['end_time'] = return_time
            emergencies[emergency_id]['assigned_vehicle_id'] = v_id

            # keep track of the emergency and set the status for the vehicles
            vehicles[v_id].emergency_status = True
            vehicles[v_id].emergency_ids.append(emergency_id)

            # adding the current location to visited_patrol_locations
            # if the vehicles was there patrolling
            if  vehicles[v_id].current_location in c.PATROL_LOCATIONS and \
                vehicles[v_id].current_location not in visited_patrol_locations and \
                vehicles[v_id].time_at_curr_location > 0:
                visited_patrol_locations.append(vehicles[v_id].current_location)

            # adjusting the route and appending the new arrival location
            vehicles[v_id].update_current_route(current_time, data, [])
            vehicles[v_id].route.append(
                [vehicles[v_id].current_location,
                 current_time+vehicles[v_id].time_to_curr_location,
                 current_time+vehicles[v_id].time_to_curr_location])
            vehicles[v_id].route.append([location, arrival_time, return_time])
            vehicles[v_id].current_location = location
            vehicles[v_id].time_to_curr_locaton = 0
            vehicles[v_id].time_at_curr_locaton = 0

            # adding the event for the end of the emergency to the event queue
            # (events will be sorted at the start of every loop)
            event_queue.append({'event_id': emergency_id,
                                'type': 'end',
                                'time': return_time,
                                'assigned': v_id})




    # updating the visited patrol locations
    visited_patrol_locations = mvf.update_vpl(visited_patrol_locations,
                                              c.PATROL_LOCATIONS,
                                              vehicles,
                                              current_time+86400) # jump full day to catch everything


    # save seed, vehicle data (including routes), visited patrol locations, emergencies
    # and demand of extra vehicles to a json file

    simulation_time = time.perf_counter() - simulation_start_time

    mvf.save_to_file(c.path,
                     seed,
                     vehicles,
                     visited_patrol_locations,
                     emergencies,
                     extra_vehicles,
                     simulation_time)
    return f"Seed {seed} done.\nCalculation took {simulation_time} seconds."



def main():
    """
    runs the simulate function
    uses multiprocessing
    """

    with concurrent.futures.ProcessPoolExecutor(max_workers=c.MAX_WORKERS) as executor:
        results = [executor.submit(run_simulation) for _ in range(c.NUMBER_OF_SIMULATIONS)]

        for future in concurrent.futures.as_completed(results):
            print(f"COMPLETED:\n{future.result()}")



if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    total_time = time.perf_counter()-start_time

    print(f"Running the simulation {c.NUMBER_OF_SIMULATIONS} time(s) took {total_time} seconds.")
