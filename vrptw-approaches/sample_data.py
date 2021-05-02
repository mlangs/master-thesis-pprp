from pprint import pprint
import random


def create_data_model():
    data = {}
    data['time_matrix'] = [
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],        # 0
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],    # 1
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],  # 2
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],  # 3
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],    # 4
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],       # 5
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],   # 6
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],       # 7
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],      # 8
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],       # 9
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],   # 10
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],    # 11
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],      # 12
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],      # 13
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],     # 14
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],  # 15
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],   # 16
    ]
    data['time_windows'] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]
    data['num_vehicles'] = 4
    data['depot'] = 0
    # data['starts'] = [1, 2, 15, 16]
    # data['ends'] = [0, 0, 0, 0]
    return data


def create_data_model_small():
    data = {}
    data['time_matrix'] = [
        [0, 6, 9, 8, 7, 3],
        [6, 0, 8, 3, 2, 6],
        [9, 8, 0, 11, 10, 6],
        [8, 3, 11, 0, 1, 7],
        [7, 2, 10, 1, 0, 6],
        [3, 6, 6, 7, 6, 0],
    ]

    data['time_windows'] = [
        (0, 5),
        (7, 12),
        (10, 15),
        (16, 18),
        (10, 13),
        (0, 5),
    ]

    data['num_vehicles'] = 2
    data['depot'] = 0
    return data


def create_data_model_dynamic(SIZE=15):

    a, b = 2, 8
    window_start_a, window_start_b = 0, 0
    window_a, window_b = 50, 50

    time_matrix = [[0 for i in range(SIZE)] for j in range(SIZE)]
    for i in range(SIZE):
        for j in range(i, SIZE):
            if i != j:
                tmp = random.randint(a, b)
                time_matrix[i][j] = tmp
                time_matrix[j][i] = tmp

    time_windows = []
    for i in range(SIZE):
        tmp = random.randint(window_start_a, window_start_b)
        time_windows.append((tmp, tmp+random.randint(window_a, window_b)))

    data = {}
    data['time_matrix'] = time_matrix

    data['time_windows'] = time_windows

    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def create_data_model_predefined():

    SIZE = 16  # SIZE % VEHICLES == 0 !!!!
    VEHICLES = 4
    a, b = 2, 4

    time_matrix = [[0 for i in range(SIZE)] for j in range(SIZE)]
    for i in range(SIZE):
        for j in range(i, SIZE):
            if i != j:
                tmp = random.randint(a, b)
                time_matrix[i][j] = tmp
                time_matrix[j][i] = tmp

    time_windows = []
    for i in range(VEHICLES):
        for j in range(SIZE // VEHICLES):
            time_windows.append((j*4, 8+j*4))

    data = {}
    data['time_matrix'] = time_matrix

    data['time_windows'] = time_windows

    data['num_vehicles'] = 4
    data['depot'] = 0
    return data


def create_data_model_large():
    data = {}
    data['time_matrix'] = [
        [0, 2, 2, 3, 2, 5, 2, 4, 3, 3, 2, 4, 4, 2, 4, 3, 5, 3, 5, 4, 2, 3, 3, 2, 4, 3,
            2, 2, 4, 3, 3, 5, 5, 4, 4, 4, 3, 2, 5, 4, 5, 5, 2, 5, 5, 2, 2, 5, 2, 5],
        [2, 0, 2, 2, 3, 4, 2, 3, 5, 4, 4, 2, 2, 5, 5, 4, 4, 5, 5, 5, 3, 5, 2, 3, 3, 5,
            2, 2, 3, 3, 4, 2, 5, 3, 5, 4, 4, 5, 3, 5, 5, 2, 4, 2, 3, 4, 3, 4, 3, 4],
        [2, 2, 0, 4, 4, 2, 2, 5, 3, 2, 2, 3, 3, 2, 4, 5, 4, 4, 4, 2, 2, 3, 4, 5, 5, 3,
            5, 5, 2, 2, 4, 5, 5, 4, 4, 5, 2, 2, 3, 2, 2, 2, 5, 4, 4, 3, 2, 4, 5, 2],
        [3, 2, 4, 0, 3, 4, 3, 2, 3, 2, 2, 4, 5, 5, 5, 3, 2, 4, 4, 4, 5, 2, 5, 5, 3, 5,
            3, 3, 4, 5, 4, 5, 4, 2, 4, 5, 2, 2, 4, 3, 2, 2, 4, 3, 4, 2, 4, 2, 4, 2],
        [2, 3, 4, 3, 0, 2, 4, 4, 3, 2, 5, 3, 5, 5, 3, 2, 3, 4, 3, 3, 2, 3, 2, 3, 4, 3,
            2, 2, 4, 4, 4, 2, 3, 4, 5, 3, 4, 5, 5, 3, 4, 3, 2, 2, 2, 3, 3, 4, 2, 2],
        [5, 4, 2, 4, 2, 0, 5, 3, 3, 4, 2, 4, 3, 3, 5, 3, 2, 2, 2, 3, 5, 3, 4, 2, 4, 4,
            3, 4, 4, 2, 2, 4, 2, 2, 3, 3, 2, 5, 2, 5, 2, 4, 3, 5, 4, 3, 2, 3, 4, 5],
        [2, 2, 2, 3, 4, 5, 0, 5, 2, 5, 3, 3, 5, 2, 4, 3, 4, 5, 2, 5, 2, 5, 4, 5, 4, 2,
            4, 5, 3, 4, 4, 3, 4, 2, 5, 3, 5, 2, 2, 5, 3, 5, 5, 3, 4, 3, 3, 2, 4, 4],
        [4, 3, 5, 2, 4, 3, 5, 0, 5, 2, 4, 5, 4, 4, 3, 3, 5, 5, 2, 5, 4, 4, 5, 4, 2, 5,
            3, 2, 3, 4, 5, 3, 5, 5, 4, 3, 2, 4, 4, 3, 2, 2, 5, 3, 3, 2, 3, 2, 2, 3],
        [3, 5, 3, 3, 3, 3, 2, 5, 0, 4, 4, 4, 2, 3, 5, 5, 3, 2, 3, 4, 2, 5, 5, 5, 3, 4,
            5, 5, 5, 5, 4, 5, 3, 2, 5, 3, 4, 2, 4, 5, 3, 3, 4, 3, 3, 3, 3, 4, 3, 2],
        [3, 4, 2, 2, 2, 4, 5, 2, 4, 0, 4, 2, 2, 5, 2, 3, 3, 3, 2, 3, 5, 3, 5, 5, 2, 3,
            5, 3, 3, 2, 2, 2, 3, 3, 5, 5, 5, 3, 3, 4, 2, 5, 3, 2, 5, 4, 3, 3, 3, 2],
        [2, 4, 2, 2, 5, 2, 3, 4, 4, 4, 0, 4, 3, 5, 4, 5, 2, 3, 3, 5, 4, 4, 5, 3, 3, 4,
            2, 3, 5, 4, 2, 4, 4, 5, 5, 3, 2, 4, 4, 4, 3, 5, 4, 4, 2, 5, 3, 4, 3, 5],
        [4, 2, 3, 4, 3, 4, 3, 5, 4, 2, 4, 0, 4, 4, 4, 4, 5, 2, 5, 4, 5, 4, 4, 5, 2, 2,
            3, 2, 4, 2, 5, 3, 5, 4, 4, 5, 5, 5, 2, 3, 4, 5, 5, 4, 3, 3, 3, 4, 5, 2],
        [4, 2, 3, 5, 5, 3, 5, 4, 2, 2, 3, 4, 0, 5, 4, 2, 4, 2, 4, 4, 2, 4, 4, 4, 2, 4,
            3, 4, 5, 5, 2, 4, 2, 3, 3, 5, 4, 2, 5, 5, 4, 4, 2, 5, 4, 5, 5, 2, 3, 5],
        [2, 5, 2, 5, 5, 3, 2, 4, 3, 5, 5, 4, 5, 0, 3, 3, 5, 2, 3, 3, 5, 2, 3, 2, 5, 2,
            2, 3, 4, 2, 3, 2, 5, 3, 4, 4, 2, 5, 4, 5, 2, 4, 4, 3, 3, 4, 5, 4, 4, 4],
        [4, 5, 4, 5, 3, 5, 4, 3, 5, 2, 4, 4, 4, 3, 0, 5, 2, 5, 2, 2, 4, 2, 3, 4, 3, 2,
            5, 2, 5, 2, 2, 2, 4, 3, 5, 4, 2, 5, 2, 3, 4, 2, 2, 2, 4, 4, 2, 5, 4, 5],
        [3, 4, 5, 3, 2, 3, 3, 3, 5, 3, 5, 4, 2, 3, 5, 0, 5, 2, 3, 4, 4, 2, 2, 4, 5, 5,
            4, 3, 5, 2, 5, 2, 2, 2, 3, 3, 2, 4, 2, 2, 2, 4, 3, 4, 2, 5, 3, 5, 4, 4],
        [5, 4, 4, 2, 3, 2, 4, 5, 3, 3, 2, 5, 4, 5, 2, 5, 0, 5, 5, 5, 2, 2, 3, 2, 5, 3,
            5, 3, 4, 2, 3, 2, 2, 5, 5, 3, 5, 2, 3, 2, 2, 4, 4, 4, 4, 2, 5, 5, 5, 4],
        [3, 5, 4, 4, 4, 2, 5, 5, 2, 3, 3, 2, 2, 2, 5, 2, 5, 0, 3, 4, 5, 5, 4, 2, 5, 4,
            4, 4, 3, 3, 5, 2, 5, 4, 2, 2, 5, 3, 3, 2, 3, 4, 3, 5, 2, 4, 5, 5, 3, 3],
        [5, 5, 4, 4, 3, 2, 2, 2, 3, 2, 3, 5, 4, 3, 2, 3, 5, 3, 0, 2, 2, 3, 2, 4, 4, 5,
            4, 3, 5, 3, 5, 3, 4, 3, 5, 5, 2, 4, 5, 2, 4, 5, 5, 4, 2, 4, 5, 3, 3, 5],
        [4, 5, 2, 4, 3, 3, 5, 5, 4, 3, 5, 4, 4, 3, 2, 4, 5, 4, 2, 0, 4, 3, 5, 5, 5, 4,
            5, 4, 4, 5, 5, 2, 4, 2, 5, 4, 4, 5, 2, 4, 5, 3, 4, 5, 4, 2, 3, 5, 5, 3],
        [2, 3, 2, 5, 2, 5, 2, 4, 2, 5, 4, 5, 2, 5, 4, 4, 2, 5, 2, 4, 0, 4, 2, 3, 5, 4,
            4, 3, 3, 3, 3, 5, 5, 4, 5, 3, 2, 5, 4, 3, 4, 3, 3, 5, 4, 4, 2, 2, 3, 3],
        [3, 5, 3, 2, 3, 3, 5, 4, 5, 3, 4, 4, 4, 2, 2, 2, 2, 5, 3, 3, 4, 0, 4, 3, 2, 4,
            4, 5, 2, 3, 2, 2, 3, 3, 2, 3, 4, 2, 3, 2, 3, 4, 2, 4, 5, 3, 4, 4, 3, 5],
        [3, 2, 4, 5, 2, 4, 4, 5, 5, 5, 5, 4, 4, 3, 3, 2, 3, 4, 2, 5, 2, 4, 0, 4, 2, 3,
            5, 3, 3, 2, 4, 4, 4, 5, 5, 4, 4, 2, 4, 5, 4, 3, 5, 3, 3, 5, 5, 3, 2, 5],
        [2, 3, 5, 5, 3, 2, 5, 4, 5, 5, 3, 5, 4, 2, 4, 4, 2, 2, 4, 5, 3, 3, 4, 0, 5, 3,
            2, 5, 3, 3, 3, 3, 3, 4, 2, 5, 4, 4, 2, 4, 3, 2, 4, 5, 2, 5, 3, 2, 3, 2],
        [4, 3, 5, 3, 4, 4, 4, 2, 3, 2, 3, 2, 2, 5, 3, 5, 5, 5, 4, 5, 5, 2, 2, 5, 0, 4,
            5, 5, 2, 5, 3, 5, 2, 2, 4, 2, 3, 2, 2, 4, 5, 4, 4, 5, 5, 3, 5, 4, 3, 4],
        [3, 5, 3, 5, 3, 4, 2, 5, 4, 3, 4, 2, 4, 2, 2, 5, 3, 4, 5, 4, 4, 4, 3, 3, 4, 0,
            4, 2, 5, 3, 3, 4, 5, 2, 4, 4, 4, 2, 4, 4, 3, 4, 2, 2, 4, 4, 4, 3, 2, 3],
        [2, 2, 5, 3, 2, 3, 4, 3, 5, 5, 2, 3, 3, 2, 5, 4, 5, 4, 4, 5, 4, 4, 5, 2, 5, 4,
            0, 3, 4, 2, 5, 3, 4, 2, 3, 3, 4, 4, 5, 2, 2, 5, 3, 5, 2, 3, 3, 3, 5, 2],
        [2, 2, 5, 3, 2, 4, 5, 2, 5, 3, 3, 2, 4, 3, 2, 3, 3, 4, 3, 4, 3, 5, 3, 5, 5, 2,
            3, 0, 5, 4, 5, 3, 5, 4, 3, 4, 3, 2, 4, 2, 4, 5, 5, 5, 3, 3, 5, 3, 5, 4],
        [4, 3, 2, 4, 4, 4, 3, 3, 5, 3, 5, 4, 5, 4, 5, 5, 4, 3, 5, 4, 3, 2, 3, 3, 2, 5,
            4, 5, 0, 2, 4, 3, 4, 2, 4, 2, 4, 5, 5, 3, 3, 2, 2, 2, 2, 5, 5, 4, 2, 4],
        [3, 3, 2, 5, 4, 2, 4, 4, 5, 2, 4, 2, 5, 2, 2, 2, 2, 3, 3, 5, 3, 3, 2, 3, 5, 3,
            2, 4, 2, 0, 5, 4, 5, 5, 4, 5, 4, 2, 4, 4, 5, 5, 5, 4, 3, 3, 5, 3, 2, 5],
        [3, 4, 4, 4, 4, 2, 4, 5, 4, 2, 2, 5, 2, 3, 2, 5, 3, 5, 5, 5, 3, 2, 4, 3, 3, 3,
            5, 5, 4, 5, 0, 3, 5, 3, 5, 5, 4, 4, 5, 3, 2, 5, 2, 4, 5, 3, 4, 5, 2, 2],
        [5, 2, 5, 5, 2, 4, 3, 3, 5, 2, 4, 3, 4, 2, 2, 2, 2, 2, 3, 2, 5, 2, 4, 3, 5, 4,
            3, 3, 3, 4, 3, 0, 3, 5, 2, 4, 2, 3, 4, 4, 5, 5, 3, 5, 4, 5, 3, 2, 2, 4],
        [5, 5, 5, 4, 3, 2, 4, 5, 3, 3, 4, 5, 2, 5, 4, 2, 2, 5, 4, 4, 5, 3, 4, 3, 2, 5,
            4, 5, 4, 5, 5, 3, 0, 4, 5, 4, 2, 5, 5, 2, 3, 4, 2, 4, 2, 4, 4, 2, 4, 5],
        [4, 3, 4, 2, 4, 2, 2, 5, 2, 3, 5, 4, 3, 3, 3, 2, 5, 4, 3, 2, 4, 3, 5, 4, 2, 2,
            2, 4, 2, 5, 3, 5, 4, 0, 5, 2, 2, 3, 2, 3, 2, 4, 3, 4, 4, 3, 4, 2, 5, 5],
        [4, 5, 4, 4, 5, 3, 5, 4, 5, 5, 5, 4, 3, 4, 5, 3, 5, 2, 5, 5, 5, 2, 5, 2, 4, 4,
            3, 3, 4, 4, 5, 2, 5, 5, 0, 5, 3, 4, 3, 4, 3, 5, 3, 4, 5, 3, 3, 3, 4, 4],
        [4, 4, 5, 5, 3, 3, 3, 3, 3, 5, 3, 5, 5, 4, 4, 3, 3, 2, 5, 4, 3, 3, 4, 5, 2, 4,
            3, 4, 2, 5, 5, 4, 4, 2, 5, 0, 4, 3, 4, 5, 4, 4, 3, 3, 2, 4, 4, 5, 4, 3],
        [3, 4, 2, 2, 4, 2, 5, 2, 4, 5, 2, 5, 4, 2, 2, 2, 5, 5, 2, 4, 2, 4, 4, 4, 3, 4,
            4, 3, 4, 4, 4, 2, 2, 2, 3, 4, 0, 4, 2, 4, 3, 4, 2, 4, 3, 2, 3, 2, 4, 4],
        [2, 5, 2, 2, 5, 5, 2, 4, 2, 3, 4, 5, 2, 5, 5, 4, 2, 3, 4, 5, 5, 2, 2, 4, 2, 2,
            4, 2, 5, 2, 4, 3, 5, 3, 4, 3, 4, 0, 5, 3, 5, 5, 2, 3, 2, 4, 3, 4, 3, 2],
        [5, 3, 3, 4, 5, 2, 2, 4, 4, 3, 4, 2, 5, 4, 2, 2, 3, 3, 5, 2, 4, 3, 4, 2, 2, 4,
            5, 4, 5, 4, 5, 4, 5, 2, 3, 4, 2, 5, 0, 3, 4, 3, 3, 5, 2, 2, 4, 4, 4, 5],
        [4, 5, 2, 3, 3, 5, 5, 3, 5, 4, 4, 3, 5, 5, 3, 2, 2, 2, 2, 4, 3, 2, 5, 4, 4, 4,
            2, 2, 3, 4, 3, 4, 2, 3, 4, 5, 4, 3, 3, 0, 4, 3, 4, 4, 2, 2, 3, 3, 5, 5],
        [5, 5, 2, 2, 4, 2, 3, 2, 3, 2, 3, 4, 4, 2, 4, 2, 2, 3, 4, 5, 4, 3, 4, 3, 5, 3,
            2, 4, 3, 5, 2, 5, 3, 2, 3, 4, 3, 5, 4, 4, 0, 4, 2, 4, 3, 5, 4, 2, 2, 4],
        [5, 2, 2, 2, 3, 4, 5, 2, 3, 5, 5, 5, 4, 4, 2, 4, 4, 4, 5, 3, 3, 4, 3, 2, 4, 4,
            5, 5, 2, 5, 5, 5, 4, 4, 5, 4, 4, 5, 3, 3, 4, 0, 3, 2, 2, 2, 3, 2, 2, 5],
        [2, 4, 5, 4, 2, 3, 5, 5, 4, 3, 4, 5, 2, 4, 2, 3, 4, 3, 5, 4, 3, 2, 5, 4, 4, 2,
            3, 5, 2, 5, 2, 3, 2, 3, 3, 3, 2, 2, 3, 4, 2, 3, 0, 2, 4, 4, 5, 5, 3, 5],
        [5, 2, 4, 3, 2, 5, 3, 3, 3, 2, 4, 4, 5, 3, 2, 4, 4, 5, 4, 5, 5, 4, 3, 5, 5, 2,
            5, 5, 2, 4, 4, 5, 4, 4, 4, 3, 4, 3, 5, 4, 4, 2, 2, 0, 3, 3, 4, 4, 4, 2],
        [5, 3, 4, 4, 2, 4, 4, 3, 3, 5, 2, 3, 4, 3, 4, 2, 4, 2, 2, 4, 4, 5, 3, 2, 5, 4,
            2, 3, 2, 3, 5, 4, 2, 4, 5, 2, 3, 2, 2, 2, 3, 2, 4, 3, 0, 2, 5, 2, 3, 5],
        [2, 4, 3, 2, 3, 3, 3, 2, 3, 4, 5, 3, 5, 4, 4, 5, 2, 4, 4, 2, 4, 3, 5, 5, 3, 4,
            3, 3, 5, 3, 3, 5, 4, 3, 3, 4, 2, 4, 2, 2, 5, 2, 4, 3, 2, 0, 3, 3, 4, 3],
        [2, 3, 2, 4, 3, 2, 3, 3, 3, 3, 3, 3, 5, 5, 2, 3, 5, 5, 5, 3, 2, 4, 5, 3, 5, 4,
            3, 5, 5, 5, 4, 3, 4, 4, 3, 4, 3, 3, 4, 3, 4, 3, 5, 4, 5, 3, 0, 3, 5, 2],
        [5, 4, 4, 2, 4, 3, 2, 2, 4, 3, 4, 4, 2, 4, 5, 5, 5, 5, 3, 5, 2, 4, 3, 2, 4, 3,
            3, 3, 4, 3, 5, 2, 2, 2, 3, 5, 2, 4, 4, 3, 2, 2, 5, 4, 2, 3, 3, 0, 5, 2],
        [2, 3, 5, 4, 2, 4, 4, 2, 3, 3, 3, 5, 3, 4, 4, 4, 5, 3, 3, 5, 3, 3, 2, 3, 3, 2,
            5, 5, 2, 2, 2, 2, 4, 5, 4, 4, 4, 3, 4, 5, 2, 2, 3, 4, 3, 4, 5, 5, 0, 2],
        [5, 4, 2, 2, 2, 5, 4, 3, 2, 2, 5, 2, 5, 4, 5, 4, 4, 3, 5, 3, 3, 5, 5, 2, 4, 3,
            2, 4, 4, 5, 2, 4, 5, 5, 4, 3, 4, 2, 5, 5, 4, 5, 5, 2, 5, 3, 2, 2, 2, 0],
    ]

    data['time_windows'] = [(0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50),
                            (0, 50)]

    data['num_vehicles'] = 5
    data['depot'] = 0
    return data
