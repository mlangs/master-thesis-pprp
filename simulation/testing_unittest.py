"""
some test cases, but not very excessive
relys on the favoriten data
"""

import unittest

import config as c
import data_favoriten as d
import mvf


class Tests(unittest.TestCase):
    """
    some test cases, but not very excessive
    """
    def test_settings(self):
        """
        some tests for the config files
        """

        # see if all start times are lower than their associated end times
        for time_window in c.TIME_WINDOWS:
            self.assertTrue(time_window[0] <= time_window[1])

        # see if the parameters are plausible
        self.assertTrue(c.NUMBER_OF_VEHICLES > 0)
        self.assertTrue(c.PATROLLING_TIME_PER_LOCATION > 0)
        self.assertTrue(c.MAX_PATROLLING_TIME_PER_VEHICLE > 0)
        self.assertFalse(c.POLICE_STATION in c.PATROL_LOCATIONS)


    def test_create_emergencies(self):
        """
        some tests for the create_emergencies function
        """
        simulation_duration = 60*60*3
        number_of_events_mu = 6
        number_of_events_sigma = 4
        time_of_event_min = 0
        time_of_event_max = simulation_duration
        event_duration_mu = 60*15
        event_duration_sigma = 60*5

        possible_locations_of_events = [17322879, 17322882, 17322883, 17322887, 17322888,
                                        17322889, 17322896, 17322899, 27027753, 27027755,
                                        27027758, 27027786, 27027934, 27027935, 27027938,
                                        27027939, 27027940, 27377265, 27377267, 27377268,
                                        29006387, 29006395, 29006403, 29006408, 29006423,
                                        29006424, 29006426, 29006430, 29006478, 29006482]

        # testing 100 times
        for _ in range(100):
            emergencies = mvf.create_emergencies(number_of_events_mu,
                                                 number_of_events_sigma,
                                                 time_of_event_min,
                                                 time_of_event_max,
                                                 event_duration_mu,
                                                 event_duration_sigma,
                                                 possible_locations_of_events)

            # correct emergency indexing
            self.assertTrue( sorted(list(emergencies.keys())) == list(range(0, len(emergencies))) )

            # start time, duration, arrival time, end time, location
            for emergency in emergencies.values():
                self.assertTrue(time_of_event_min <= emergency['start_time'] <= time_of_event_max)
                self.assertTrue(emergency['duration'] >= 0)
                self.assertTrue(emergency['arrival_time'] is None)
                self.assertTrue(emergency['end_time'] is None)
                self.assertTrue(emergency['assigned_vehicle_id'] is None)
                self.assertTrue(emergency['location'] in possible_locations_of_events)


    def test_update_locations_and_windows(self):
        """
        some tests for the update_locations_and_windows function
        """
        patrol_locations = [3674544936,
                            298161859,
                            61832953,
                            597465575]
        time_windows = [
                        (0, 60*60*3),	# 0
                        (0, 60*60*3),	# 1
                        (0, 60*60*3),	# 2
                        (0, 60*60*3),	# 3
                        ]
        police_station = 17322882
        patrolling_time_per_location = 3*60

        vehicles = [mvf.Vehicle(i, None) for i in range(6)]

        vehicles[0].current_location = 3674544936
        vehicles[0].time_to_curr_location = 5
        vehicles[0].time_at_curr_location = 0

        vehicles[1].current_location = 298161859
        vehicles[1].time_to_curr_location = 0
        vehicles[1].time_at_curr_location = 60

        vehicles[2].current_location = 61832953
        vehicles[2].time_to_curr_location = 0
        vehicles[2].time_at_curr_location = 3*60

        vehicles[3].current_location = 1234
        vehicles[3].time_to_curr_location = 50
        vehicles[3].time_at_curr_location = 0

        vehicles[4].current_location = 1234
        vehicles[4].time_to_curr_location = 0
        vehicles[4].time_at_curr_location = 0

        # actually impossible to have two vehicles patrolling at the same location
        vehicles[5].current_location = 298161859
        vehicles[5].time_to_curr_location = 0
        vehicles[5].time_at_curr_location = 65

        locations_and_windows = mvf.update_locations_and_windows(patrol_locations,
                                                                 time_windows,
                                                                 vehicles,
                                                                 police_station,
                                                                 patrolling_time_per_location)
        starts, dummy_locations, updated_patrol_locations, time_windows = locations_and_windows

        self.assertTrue(starts == [3674544936, 298161859, 61832953, 1234, 1234, 298161859])
        self.assertTrue(dummy_locations == [[5, 1234], [6, 1234], [7, 298161859]])
        self.assertTrue(updated_patrol_locations == [17322882,      # police station
                                                     3674544936,    # patrol location
                                                     298161859,     # patrol location
                                                     61832953,      # patrol location
                                                     597465575,     # patrol location
                                                     1234,          # dummy location
                                                     1234,          # dummy location
                                                     298161859      # dummy location
                                                     ])

        self.assertTrue(time_windows == [(0, 86400),
                                         (185, 185),
                                         (120, 120), #
                                         (0, 0),
                                         (0, 60*60*3),
                                         (50, 50),
                                         (0, 0),
                                         (0, 0)]) #



    def test_create_data_model(self):
        """
        some tests for the create_data_model function
        """
        patrol_locations = [3835886950, 34516819, 61831215]
        updated_patrol_locations = [17322884, 3835886950, 34516819, 61831215,
                                    17322884, 61832281, 17322884]
        time_windows = [(0, 86400), (0, 2629), (0, 2629), (0, 2629),
                        (0, 86400), (0, 0), (0, 86400)]
        starts =  [17322884, 61832281, 17322884, 3835886950]
        dummy_locations = [[4, 17322884], [5, 61832281], [6, 17322884]]
        police_station = 17322884

        time_matrix = d.time_matrix
        osm_to_index = d.osm_to_index

        expected_data = {
            'osm_to_index': {17322884: 0, 3835886950: 1, 34516819: 2, 61831215: 3},
            'index_to_osm': {0: 17322884, 1: 3835886950, 2: 34516819,
                             3: 61831215, 4: 17322884, 5: 61832281, 6: 17322884},
            'time_matrix': [[0, 97, 50, 46, 0, 122, 0], [88, 0, 38, 42, 88, 110, 88],
                            [50, 54, 0, 4, 50, 119, 50], [46, 58, 4, 0, 46, 123, 46],
                            [0, 97, 50, 46, 0, 122, 0], [151, 89, 101, 105, 151, 0, 151],
                            [0, 97, 50, 46, 0, 122, 0]],
            'time_windows': [(0, 86400), (0, 2629), (0, 2629), (0, 2629),
                             (0, 86400), (0, 0), (0, 86400)],
            'num_vehicles': 4,
            'police_station': 0,
            'starts': [4, 5, 6, 1],
            'ends': [0, 0, 0, 0]}

        data = mvf.create_data_model(patrol_locations,
                                     updated_patrol_locations,
                                     time_windows,
                                     starts,
                                     dummy_locations,
                                     police_station,
                                     time_matrix,
                                     osm_to_index)

        self.assertTrue(isinstance(data, dict))
        self.assertTrue(data['osm_to_index'] == expected_data['osm_to_index'])
        self.assertTrue(data['index_to_osm'] == expected_data['index_to_osm'])
        self.assertTrue(data['time_matrix'] == expected_data['time_matrix'])
        self.assertTrue(data['time_windows'] == expected_data['time_windows'])
        self.assertTrue(data['num_vehicles'] == expected_data['num_vehicles'])
        self.assertTrue(data['police_station'] == expected_data['police_station'])
        self.assertTrue(data['starts'] == expected_data['starts'])
        self.assertTrue(data['ends'] == expected_data['ends'])



    def test_update_patrol_locations_and_time_windows(self):
        """
        some tests for the update_patrol_locations_and_time_windows function
        """
        patrol_locations = [17322879, 17322882, 17322883, 17322887, 17322888,
                            17322889, 17322896, 17322899, 27027753, 27027755]
        time_windows = [
            (80, 60*60*3),	# 0
            (0, 60*60*3),	# 1
            (0, 60*60*3),	# 2
            (0, 60*60*3),	# 3
            (0, 60*60*3),	# 4
            (0, 60*60*3),	# 5
            (0, 60*60*3),	# 6
            (0, 76),	    # 7
            (0, 74),	    # 8
            (0, 75),	    # 9
            ]

        visited_patrol_locations = [17322883, 17322896, 17322879]
        current_time = 75
        new_patrol_locations, new_time_windows =  mvf.update_patrol_locations_and_time_windows(
                                                    patrol_locations,
                                                    time_windows,
                                                    visited_patrol_locations,
                                                    current_time)

        # correct length for this example
        self.assertTrue(len(new_patrol_locations) == 5)
        self.assertTrue(len(new_time_windows) == 5)

        # visited locations not in new list
        for vpl in visited_patrol_locations:
            self.assertFalse(vpl in new_patrol_locations)

        # edge timings
        self.assertTrue(17322899 in new_patrol_locations)
        self.assertFalse(27027755 in new_patrol_locations)
        self.assertFalse(27027753 in new_patrol_locations)

        # time windows
        for patrol_location, time_window in zip(new_patrol_locations, new_time_windows):
            idx = patrol_locations.index(patrol_location)

            # start time
            self.assertTrue(0 <= time_window[0])
            self.assertTrue(time_window[0] == max(0, time_windows[idx][0]))

            # end time
            self.assertTrue(time_window[1] == time_windows[idx][1]-current_time)



    def test_vehicle_class_update(self):
        """
        some tests for the update function in the Vehicle class
        """
        start = 17322884
        v_id = 1

        # current_time, location, time_to_curr_location, time_at_curr_location
        test_data = [[0,    start,      0,  0],
                     [34,   103664213,  1,  0],
                     [35,   103664213,  0,  0],
                     [36,   103664213,  0,  1],
                     [428,  293281751,  0,  179],
                     [429,  293281751,  0,  180],
                     [430,  53171130,   10, 0],
                     [500,  1829857697, 0,  19],
                     [1000, 1829857697, 0,  339]]

        for current_time, location, time_to_curr_location, time_at_curr_location in test_data:
            v = mvf.Vehicle(v_id, start)

            v.route = [[17322884,   0,      0],
                       [103664213,  35,     215],
                       [293281751,  249,    429],
                       [1829857697, 481,    661]]

            v.update(current_time, d.time_matrix, d.osm_to_index, c.path)
            self.assertTrue(v.current_location == location)
            self.assertTrue(v.time_to_curr_location == time_to_curr_location)
            self.assertTrue(v.time_at_curr_location == time_at_curr_location)



    def test_vehicle_class_update_current_route(self):
        """
        some tests for the update_current_route function in the Vehicle class
        """
        start = 17322884
        v_id = 0

        v = mvf.Vehicle(v_id, start)
        v.route = [[17322884,   0,      0],
                   [103664213,  35,     215],
                   [293281751,  249,    429],
                   [1829857697, 481,    661]]

        current_time=34
        new_route = [[1,  1,     1],
                     [0,   36,     36]]
        result_route = [[17322884,   0,      0],
                        [103664213,  35,     35],
                        [17322884,   70,     70]]
        data = {'index_to_osm': {0:17322884, 1:103664213, 2:293281751, 3:1829857697}}

        v.update(current_time, d.time_matrix, d.osm_to_index, c.path)
        v.update_current_route(current_time, data, new_route)


        self.assertTrue(v.old_routes == [[[17322884,   0,      0],
                                          [103664213,  35,     215],
                                          [293281751,  249,    429],
                                          [1829857697, 481,    661]]])
        self.assertTrue(v.route == result_route)


        # special case where or-tools increases the time windows because of patrolling time
        # only small change in the new_route array
        start = 17322884
        v_id = 0
        v.time_to_curr_location = 1

        v = mvf.Vehicle(v_id, start)
        v.route = [[17322884,   0,      0],
                   [103664213,  35,     215],
                   [293281751,  249,    429],
                   [1829857697, 481,    661]]

        current_time=34
        new_route = [[1,  0,     1], # should be [1,1,1] again
                     [0,   36,     36]]
        result_route = [[17322884,   0,      0],
                        [103664213,  35,     35],
                        [17322884,   70,     70]]
        data = {'index_to_osm': {0:17322884, 1:103664213, 2:293281751, 3:1829857697}}

        v.update(current_time, d.time_matrix, d.osm_to_index, c.path)
        v.update_current_route(current_time, data, new_route)


        self.assertTrue(v.old_routes == [[[17322884,   0,      0],
                                          [103664213,  35,     215],
                                          [293281751,  249,    429],
                                          [1829857697, 481,    661]]])
        self.assertTrue(v.route == result_route)



    def test_choose_response_vehicle(self):
        """
        some tests for the choose_response_vehicle function
        """
        current_time = 34
        vehicles = [mvf.Vehicle(0, 293281751), mvf.Vehicle(1, 17322884)]
        vehicles[0].route =[[293281751, 0, 0]]
        vehicles[1].route = [[17322884,   0,      0],
                             [103664213,  35,     215],
                             [293281751,  249,    429],
                             [1829857697, 481,    661]]

        emergencies = {0: {"start_time": 34,
                           "duration": 10,
                           "arrival_time": None,
                           "end_time": None,
                           "assigned_vehicle_id": None,
                           "location": 103664213}}

        for v in vehicles:
            v.update(current_time, d.time_matrix, d.osm_to_index, c.path)

        v_id, arrival_time, return_time = mvf.choose_response_vehicle(emergencies[0],
                                                                      vehicles,
                                                                      current_time,
                                                                      d.time_matrix,
                                                                      d.osm_to_index,
                                                                      method='fastest')
        self.assertTrue(v_id == 1)
        self.assertTrue(arrival_time == 35)
        self.assertTrue(return_time == 45)



    def test_update_vpl(self):
        """
        some tests for the update_vpl function
        """
        result_visited_patrol_locations = [103664213]

        vehicles = [mvf.Vehicle(0, 103664213)]
        vehicles[0].route = [[17322884,   0,      0],
                             [103664213,  35,     215],
                             [293281751,  249,    429],
                             [1829857697, 481,    661]]
        patrol_locations = [103664213, 293281751]
        visited_patrol_locations = []
        current_time = 216

        visited_patrol_locations = mvf.update_vpl(visited_patrol_locations,
                                                  patrol_locations,
                                                  vehicles,
                                                  current_time)

        self.assertTrue(visited_patrol_locations == result_visited_patrol_locations)



if __name__ == '__main__':
    unittest.main()
