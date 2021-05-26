from favoriten_data import time_matrix
from favoriten_data import distance_matrix
import matplotlib.pyplot as plt
from collections import Counter
import itertools


for matrix in [time_matrix, distance_matrix]:
    chained_matrix = [item for item in itertools.chain(*matrix)]

    counted = dict(Counter(chained_matrix))

    # remove diagonal zeros
    counted[0] -= len(matrix)
    # time matrix still countains 12 zeros
    print(f"Count of 0s which are not on the diagnonal: {counted[0]}")
    print(f"Maximum value: {max(chained_matrix)}")

    x = counted.keys()
    y = counted.values()
    plt.scatter(x, y, marker='.', s=1, c='r')

    plt.title('frequency')
    plt.show()
