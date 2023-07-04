"""
ortools functions
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def print_solution(data, manager, routing, solution):
    """
    Prints solution on console.
    """

    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Route for vehicle {vehicle_id}:\n'
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += f'{manager.IndexToNode(index)} Time({solution.Min(time_var)},{solution.Max(time_var)}) -> '
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += f'{manager.IndexToNode(index)} Time({solution.Min(time_var)},{solution.Max(time_var)})\n'
        plan_output += f'Time of the route: {solution.Min(time_var)}sec\n'
        print(plan_output)
        total_time += solution.Min(time_var)
    print(f'Total time of all routes: {total_time}sec')



def get_routes(data, manager, routing, solution, patrolling_time_per_location):
    """
    formats the route data for further processing
    """

    route_data = {}
    total_time = 0
    time_dimension = routing.GetDimensionOrDie('Time')
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            # patrolling_time_per_location needs to be subtracted!
            route.append((manager.IndexToNode(index),
                          max(solution.Min(time_var)-patrolling_time_per_location, 0),
                          solution.Max(time_var)))
            index = solution.Value(routing.NextVar(index))

        time_var = time_dimension.CumulVar(index)
        route.append((manager.IndexToNode(index), solution.Min(time_var),
                      solution.Max(time_var)))
        total_time += solution.Min(time_var)
        route_data[vehicle_id] = route
    route_data["total_time"] = total_time
    return route_data



def plan_routes(data, max_patrolling_time_per_vehicle, patrolling_time_per_location,
                firstsolutionstategy, localsearchmetaheuristic,
                solution_limit, time_limit):
    """
    solves the VRP with time windows.
    """

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'],
                                           data['starts'],
                                           data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """
        returns the travel time between the two nodes
        """
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        if to_node == data['police_station']:  # no patrolling time at the police station
            return data['time_matrix'][from_node][to_node]
        else:
            return data['time_matrix'][from_node][to_node] + patrolling_time_per_location

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc. can be changed if vehicles have different travel speed etc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = 'Time' # dimension name
    routing.AddDimension(
        transit_callback_index,
        0, # allows waiting time, not relevant with time window like (0, SIMULATION_DURATION)
        max_patrolling_time_per_vehicle,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)

    # Allow to drop nodes.
    penalty = 86400  # (1 day)
    for node in range(1, len(data['time_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # The method SetGlobalSpanCostCoefficient sets a large coefficient (100)
    # for the global span of the routes, which in this example is the maximum
    # of the distances of the routes. This makes the global span the predominant
    # factor in the objective function, so the program minimizes the length
    # of the longest route.
    # [sets] a cost proportional to the global dimension span, that is the
    # difference between the largest value of route end cumul variables and
    # the smallest value of route start cumul variables. In other words:
    # global_span_cost = coefficient * (Max(dimension end value) - Min(dimension start value)).
    # time_dimension.SetGlobalSpanCostCoefficient(100)

    # This line limits vehicle driving time to x minutes without considering start time
    for vehicle_id in range(data['num_vehicles']):
        time_dimension.SetSpanUpperBoundForVehicle(max_patrolling_time_per_vehicle, vehicle_id)

    # Add time window constraints for each location except for the police station.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['police_station']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][data['starts'][vehicle_id]][0],
                                                data['time_windows'][data['starts'][vehicle_id]][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.log_search = False


    first_solution_options = {'UNSET': 0,
                              'AUTOMATIC': 15,
                              'PATH_CHEAPEST_ARC': 3,
                              'PATH_MOST_CONSTRAINED_ARC': 4,
                              'EVALUATOR_STRATEGY': 5,
                              'SAVINGS': 10,
                              'SWEEP': 11,
                              'CHRISTOFIDES': 13,
                              'ALL_UNPERFORMED': 6,
                              'BEST_INSERTION': 7,
                              'PARALLEL_CHEAPEST_INSERTION': 8,
                              'SEQUENTIAL_CHEAPEST_INSERTION': 14,
                              'LOCAL_CHEAPEST_INSERTION': 9,
                              'GLOBAL_CHEAPEST_ARC': 1,
                              'LOCAL_CHEAPEST_ARC': 2,
                              'FIRST_UNBOUND_MIN_VALUE': 12}

    if firstsolutionstategy in first_solution_options:
        search_parameters.first_solution_strategy = (
            first_solution_options[firstsolutionstategy])
    else:
        raise ValueError('Missing or wrong firstsolutionstategy')
    #search_parameters.first_solution_strategy = (
    #    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)

    local_search_metaheuristic_options = {'UNSET': 0,
                                          'AUTOMATIC': 6,
                                          'GREEDY_DESCENT': 1,
                                          'GUIDED_LOCAL_SEARCH': 2,
                                          'SIMULATED_ANNEALING': 3,
                                          'TABU_SEARCH': 4,
                                          'GENERIC_TABU_SEARCH': 5}
    if localsearchmetaheuristic in local_search_metaheuristic_options:
        search_parameters.local_search_metaheuristic =(
            local_search_metaheuristic_options[localsearchmetaheuristic])
    else:
        raise ValueError('Missing or wrong localsearchmetaheuristic')
    #search_parameters.local_search_metaheuristic = (
    #    routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT)

    # set a time limit of x seconds for a search
    search_parameters.time_limit.seconds = time_limit

    # set a solution limit of x for a search
    search_parameters.solution_limit = solution_limit

    # print(search_parameters)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # print_solution(data, manager, routing, solution)
        return get_routes(data, manager, routing, solution, patrolling_time_per_location)
    else:
        print('No solution found !')



if __name__ == '__main__':
    print("please do not run as main")
