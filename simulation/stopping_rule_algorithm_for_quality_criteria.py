from pathlib import Path

import scipy.stats
import osmnx as ox
import pandas as pd

from main import main as run_simulation_batch

def gauss_stopping_rule(delta, p, M, sigma2):
    phi = scipy.stats.norm().cdf(-(M**.5) * delta/(sigma2**.5))
    return (1-p) - 2*phi >= 0


def chebyshev_stopping_rule(delta, p, M, sigma2):
    return (1-p) - sigma2/(M*delta**2) >= 0


def algorithm2(df, path, p, delta, M_0, variable, max_i=None, start_i=0, X_avg=None, X2_avg=None):
    if X_avg is None:
        X_avg = [0]
        X2_avg = [0]

    i = start_i
    while True:
        i += 1
        try:
            X = df[variable][i-1]
        except:
            print('not enough data in the .csv file')
            return False, i-1, X_avg, X2_avg, False

        X_i = ((i-1)/i)*X_avg[-1] + (1/i)*X
        X_avg.append(X_i)

        X2_i = ((i-1)/i)*X2_avg[-1] + (1/i)*X**2
        X2_avg.append(X2_i)

        if i > max_i:
            return False, i-1, X_avg, X2_avg, False
        if i <= M_0:
            continue

        s2 = (i/(i-1))*(X2_i-X_i**2)

        # if gauss_stopping_rule(delta, p, i, s2):
        if chebyshev_stopping_rule(delta, p, i, s2):
            return True, i, X_avg, X2_avg, s2


def main():
    path = Path(__file__).parent.absolute()
    folder = '04'

    # calculation_time
    # p, delta_abs, M_0 = 0.95, 3, 100
    # variable = 'calculation_time'
    # True 1356 48.29451841629441 2941.821768528324 609.9110463738795


    #### Emergencies
    # number of missed emergencies
    # p, delta_abs, M_0 = 0.95, 0.05, 100
    # variable = 'n_missed_emergencies'
    # True 492 0.04268292682926833 0.06300813008130082 0.06131091351646714
    # True 1716 0.04254079254079257 0.055361305361305346 0.053582811746077035

    # response time avg?
    # p, delta_abs, M_0 = 0.95, 3, 100
    # variable = 'reaction_times'


    #### Patrols
    # number of visited patrol locations
    # p, delta_abs, M_0 = 0.95, 0.000000204, 100
    # variable = 'n_visited_patrol_locations'
    # True 111 30.000000000000004 900.0000000000005 2.2944070885635234e-13

    # map coverage
    # p, delta_abs, M_0 = 0.95, 0.005, 100
    # variable = 'coverage'
    # True 599 0.17467086129299086 0.03125580469511261 0.0007471422261808313

    #### Resources
    # number of emergencies
    # p, delta_abs, M_0 = 0.95, 0.5, 100
    # variable = 'n_emergencies'
    # True 1008 6.38690476190477 53.36309523809526 12.583025961129161

    # total_travelled_distance
    # p, delta_abs, M_0 = 0.95, 2000, 100
    # variable = 'total_travelled_distance'
    # True 1951 63345.26123833922 4402336919.649329 389914652.0386037

    # total_travelled_time
    # p, delta_abs, M_0 = 0.95, 450, 100
    # variable = 'total_travelled_time'
    # True 1591 27783.790697674376 788021334.9509724 16092424.07880705

    max_i = 2000

    files = path.glob(f"output/432/{folder}/simulation.csv")
    df = pd.read_csv(list(files)[0])

    # files = sorted(path.glob(f"output/432/{folder}/simulation.json"))
    # file_count = len(list(files))
    # print(f"file_count: {file_count}\n")

    finished, start_i, X_avg, X2_avg, s2 = algorithm2(df, path, p, delta_abs, M_0, variable, max_i)
    if finished:
        print(finished, start_i, X_avg[-1], X2_avg[-1], s2)
        return

    print("not finished")
    print(finished, start_i, X_avg[-1], X2_avg[-1], s2)
    exit()
    while start_i < max_i:
        run_simulation_batch()
        # files = sorted(path.glob("output/*.json"))
        finished, start_i, X_avg, X2_avg, s2 = algorithm2(
            df, path, p, delta_abs, M_0, variable, max_i, start_i, X_avg, X2_avg)
        if finished:
            print(finished, start_i, X_avg[-1], X2_avg[-1], s2)
            return

    print(finished, start_i, X_avg[-1], X2_avg[-1], s2)

if __name__ == '__main__':
    main()
