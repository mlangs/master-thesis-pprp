import gurobipy as gp
from gurobipy import GRB
import itertools
from sample_data import *


def print_solution(data, model, X, S, V, N):
    """Prints solution on console."""
    result = []
    for k in V:
        tmp = []
        for i in N:
            for j in N:
                if X[i][j][k]:
                    if model.getVarByName(f"x_{i}_{j}_{k}").X != 0:
                        tmp.append((i, j, model.getVarByName(f"S_{i}_{k}").X))

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
    data = create_data_model_predefined()

    model = gp.Model()  # can be named if string is given, example "mip1"

    # precessor, successor, route
    n = len(data['time_matrix']) - 1  # number of customers
    data = add_n1(data)  # add start node as final node to the time_matrix
    C = [i for i in range(1, n+1)]    # set of all customers
    N = [i for i in range(0, n+2)]  # set of all nodes (C' = C + {0} + {n+1})
    V = [i for i in range(0, data['num_vehicles'])]  # Vehicles
    M = max([max([data['time_windows'][i][1] - data['time_windows'][i]
                  [0] + data['time_matrix'][i][j] for i in N]) for j in N])

    X = [[[0 if (i == j) else model.addVar(0, 1, vtype=GRB.INTEGER, name=f"x_{i}_{j}_{k}")
           for k in V] for j in N] for i in N]

    S = [[model.addVar(data['time_windows'][i][0], data['time_windows']
                       [i][1], vtype=GRB.INTEGER, name=f"S_{i}_{k}") for k in V] for i in N]

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
    model.setObjective(total_cost(X, S), GRB.MINIMIZE)

    # every customer should only be visited once
    def every_customer_only_once(X, c):
        s = 0
        for j, k in itertools.product(N, V):
            s += X[c][j][k]
        return s

    for customer in C:
        model.addConstr(every_customer_only_once(X, customer) == 1)

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
        model.addConstr(all_leave(X, k) == 1)
        model.addConstr(all_come_back(X, k) == 1)
        for customer in C:
            model.addConstr(exit_enter(X, k, customer) == 0)

    # time windows
    for i, j, k in itertools.product(N, N, V):
        model.addConstr((S[i][k] + data['time_matrix'][i][j] - M *
                         (1-X[i][j][k])) <= S[j][k])  # linearised
        # model.Add(X[i][j][k] * (S[i][k] + data['time_matrix']
        #                         [i][j] - S[j][k]) <= 0)  # not linearised

    model.Params.TimeLimit = 6

    # Algorithm used to solve continuous models or the root node of a MIP model.
    # Options are:
    # (DEFAULT) -1=automatic, 0=primal simplex, 1=dual simplex, 2=barrier,
    # 3=concurrent, 4=deterministic concurrent, 5=deterministic concurrent
    # simplex.
    model.Params.method = 2
    model.optimize()

    print_solution(data, model, X, S, V, N)


if __name__ == '__main__':
    main()
