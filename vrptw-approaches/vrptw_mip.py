from ortools.linear_solver import pywraplp
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
                    if X[i][j][k].solution_value() != 0:
                        tmp.append((i, j, S[i][k].solution_value()))

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
    # data = create_data_model_large()  # 50
    # data = create_data_model_dynamic(SIZE=40)
    # data = create_data_model_predefined()

    # solver = pywraplp.Solver.CreateSolver('GLOP') # geht irgendwie nicht?! variablen nehmen nicht-integer werte an
    # solver = pywraplp.Solver.CreateSolver('CLP')  # solution too small
    # solver = pywraplp.Solver.CreateSolver('GLPK')  # not working
    # solver = pywraplp.Solver.CreateSolver('CPLEX') # not working
    # solver = pywraplp.Solver.CreateSolver('GUROBI_LP')
    # solver = pywraplp.Solver.CreateSolver('GUROBI')
    """
    - CLP_LINEAR_PROGRAMMING or CLP
    - CBC_MIXED_INTEGER_PROGRAMMING or CBC
    - GLOP_LINEAR_PROGRAMMING or GLOP
    - BOP_INTEGER_PROGRAMMING or BOP
    - SAT_INTEGER_PROGRAMMING or SAT or CP_SAT
    - SCIP_MIXED_INTEGER_PROGRAMMING or SCIP
    - GUROBI_LINEAR_PROGRAMMING or GUROBI_LP
    - GUROBI_MIXED_INTEGER_PROGRAMMING or GUROBI or GUROBI_MIP
    - CPLEX_LINEAR_PROGRAMMING or CPLEX_LP
    - CPLEX_MIXED_INTEGER_PROGRAMMING or CPLEX or CPLEX_MIP
    - XPRESS_LINEAR_PROGRAMMING or XPRESS_LP
    - XPRESS_MIXED_INTEGER_PROGRAMMING or XPRESS or XPRESS_MIP
    - GLPK_LINEAR_PROGRAMMING or GLPK_LP
    - GLPK_MIXED_INTEGER_PROGRAMMING or GLPK or GLPK_MIP
    """

    # Coin-or branch and cut , https://www.coin-or.org/
    solver = pywraplp.Solver.CreateSolver('CBC')
    solver = pywraplp.Solver.CreateSolver('BOP')  # Boolean MIPs
    solver = pywraplp.Solver.CreateSolver('SAT')  # 'CP-SAT'
    solver = pywraplp.Solver.CreateSolver('SCIP')  # https://www.scipopt.org/

    # precessor, successor, route
    n = len(data['time_matrix']) - 1  # number of customers
    data = add_n1(data)  # add start node as final node to the time_matrix
    C = [i for i in range(1, n+1)]    # set of all customers
    N = [i for i in range(0, n+2)]  # set of all nodes (C' = C + {0} + {n+1})
    V = [i for i in range(0, data['num_vehicles'])]  # Vehicles
    M = max([max([data['time_windows'][i][1] - data['time_windows'][i]
                  [0] + data['time_matrix'][i][j] for i in N]) for j in N])

    X = [[[0 if (i == j) else solver.IntVar(0, 1, f"x_{i}_{j}_{k}")
           for k in V] for j in N] for i in N]

    S = [[solver.IntVar(data['time_windows'][i][0], data['time_windows']
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

    # every customer should only be visited once
    def every_customer_only_once(X, c):
        s = 0
        for j, k in itertools.product(N, V):
            s += X[c][j][k]
        return s

    for customer in C:
        solver.Add(every_customer_only_once(X, customer) == 1)

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
        solver.Add(all_leave(X, k) == 1)
        solver.Add(all_come_back(X, k) == 1)
        for customer in C:
            solver.Add(exit_enter(X, k, customer) == 0)

    # time windows
    for i, j, k in itertools.product(N, N, V):
        solver.Add((S[i][k] + data['time_matrix'][i][j] - M *
                    (1-X[i][j][k])) <= S[j][k])  # linearised
        # model.Add(X[i][j][k] * (S[i][k] + data['time_matrix']
        #                         [i][j] - S[j][k]) <= 0)  # not linearised

    # what should be optimized
    solver.Minimize(total_cost(X, S))
    print('Number of constraints =', solver.NumConstraints())

    # time limit
    # solver.SetTimeLimit = 10  # in ms? sould work but does not..
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Objective value =', solver.Objective().Value())
        print_solution(data, solver, X, S, V, N)
    elif status == pywraplp.Solver.FEASIBLE:
        print("Some solutions found!\n")
        print('Objective value =', solver.Objective().Value())
        print_solution(data, solver, X, S, V, N)
    else:
        print("No solution could be found!")


if __name__ == '__main__':
    main()
