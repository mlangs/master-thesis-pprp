"""
selecting a random sample of unique network nodes close to amenities
"""
from pathlib import Path
from collections import Counter

import pandas as pd

import data_favoriten as d

# so pandas does not hide columns in the terminal
pd.options.display.width = 0

path = Path(__file__).parent.absolute()

# getting the point of interest data
pois = pd.read_csv(path / 'pois_with nearest node.csv')
# print(pois.head())

# counting to see which amenities are represented
c = Counter(pois['amenity'])
print(c)

police_stations = pois[pois['amenity'].isin(['police'])]
print(police_stations)
print(police_stations.nearest_network_node.tolist())

# select relevant tags
tags = ['atm', 'bank', 'bar', 'biergarten', 'brothel',
        'cafe', 'casino', 'cinema', 'community_centre',
        'events_venue', 'fast_food', 'food_court',
        'gambling', 'internet_cafe', 'marketplace',
        'money_transfer', 'place_of_worship', 'pub',
        'restaurant', 'social_facility', 'theatre', 'toilets']

# remove rows with other tags
pois = pois[pois['amenity'].isin(tags)]
# print(pois.shape)

# remove entries with nodes that are removed from the network
pois = pois[~pois['nearest_network_node'].isin(d.index_to_removed_osm.values())]

# remove duplicate entries
pois.drop_duplicates(['nearest_network_node'], inplace=True)

# select sample nodes
sample = pois.sample(n=30)
# print(sample.head())

# get nearest network nodes as list
patrol_locations = sample.nearest_network_node.tolist()
print('sample patrol locations:')
print(patrol_locations)
