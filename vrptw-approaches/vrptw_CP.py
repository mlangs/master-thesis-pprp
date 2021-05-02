from ortools.sat.python import cp_model
import itertools
from sample_data import *


def print_solution(data, solver, X, S, V, N):
    """Prints solution on console."""
    result = []
    for k in V:
        tmp = []
        for i in N:
            for j in N:
                if X[i][j][k]:
                    if solver.Value(X[i][j][k]) != 0:
                        tmp.append((i, j, solver.Value(S[i][k])))

        result.append(sorted(tmp, key=lambda tuple: tuple[2]))

    total_time = 0
    for k in V:
        plan_output = 'Route for vehicle {}:\n'.format(k)

        routing = []
        for step in result[k]:
            routing.append('{0} Time({1},{2}))'.format(
                step[0], step[2], step[2]))

        time_home = result[k][-1][2] + data['time_matrix'][result[k][-1][0]][result[k][-1][1]]
        routing.append('{0} Time({1},{2}))'.format(step[1], time_home, time_home))
        plan_output += " -> ".join(routing)
        plan_output += '\nTime of the route: {}min\n'.format(time_home)
        print(plan_output)
        total_time += time_home
    print('Total time of all routes: {}min'.format(total_time))


def add_n1(data):
    for row in data['time_matrix']:
        row.append(row[0])
    data['time_matrix'].append(data['time_matrix'][0])

    data['time_windows'].append((0, 50))
    return data


def main():
    # data = create_data_model()
    data = create_data_model_small()
    # data = create_data_model_large() # 50
    # data = create_data_model_dynamic(SIZE=40)
    # data = create_data_model_predefined()

    model = cp_model.CpModel()

    # precessor, successor, route
    n = len(data['time_matrix']) - 1  # number of customers
    data = add_n1(data)  # add start node as final node to the time_matrix
    C = [i for i in range(1, n+1)]    # set of all customers
    N = [i for i in range(0, n+2)]  # set of all nodes (C' = C + {0} + {n+1})
    V = [i for i in range(0, data['num_vehicles'])]  # Vehicles
    M = max([max([data['time_windows'][i][1] - data['time_windows'][i]
                  [0] + data['time_matrix'][i][j] for i in N]) for j in N])

    X = [[[0 if (i == j) else model.NewIntVar(0, 1, f"x_{i}_{j}_{k}")
           for k in V] for j in N] for i in N]

    S = [[model.NewIntVar(data['time_windows'][i][0], data['time_windows']
                          [i][1], f"S_{i}_{k}") for k in V] for i in N]

    # total time spend
    def total_cost(X, S):
        cost = 0
        for i, j, k in itertools.product(N, N, V):
            cost += data['time_matrix'][i][j]*X[i][j][k]

        # adding time cost
        for k in V:
            cost += S[N[-1]][k]
        return cost

    # what should be optimized
    model.Minimize(total_cost(X, S))

    # every customer should only be visited once
    def every_customer_only_once(X, c):
        s = 0
        for j, k in itertools.product(N, V):
            s += X[c][j][k]
        return s

    for customer in C:
        model.Add(every_customer_only_once(X, customer) == 1)

    # flow constraints
    def all_leave(X, k):
        s = 0
        for j in N:
            s += X[0][j][k]
        return s

    def all_come_back(X, k):
        s = 0
        for i in N:
            s += X[i][n+1][k]
        return s

    def exit_enter(X, k, customer):
        x = sum([X[i][customer][k] for i in N])
        y = sum([X[customer][j][k] for j in N])
        return x-y

    for k in V:
        model.Add(all_leave(X, k) == 1)
        model.Add(all_come_back(X, k) == 1)
        for customer in C:
            model.Add(exit_enter(X, k, customer) == 0)

    # time windows
    for i, j, k in itertools.product(N, N, V):
        model.Add((S[i][k] + data['time_matrix'][i][j] - M *
                   (1-X[i][j][k])) <= S[j][k])  # linearised
        # model.Add(X[i][j][k] * (S[i][k] + data['time_matrix']
        #                         [i][j] - S[j][k]) <= 0)  # not linearised

    solver = cp_model.CpSolver()
    # time limit
    solver.parameters.max_time_in_seconds = 60.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Maximum of objective function: %i' % solver.ObjectiveValue())
        print_solution(data, solver, X, S, V, N)
    elif status == cp_model.FEASIBLE:
        print("Some solutions found!\n")
        print('Maximum of objective function: %i' % solver.ObjectiveValue())
        print_solution(data, solver, X, S, V, N)
    else:
        print("No solution could be found!")


if __name__ == '__main__':
    main()
