import unittest

import config as c
import data_favoriten as d
import mvf



class Tests(unittest.TestCase):

    def test_settings(self):
        # see if all start times are lower than their associated end times
        for time_window in c.TIME_WINDOWS:
            self.assertTrue(time_window[0] <= time_window[1])

        # are the parameters correct?
        self.assertTrue(c.NUMBER_OF_VEHICLES > 0)
        self.assertTrue(c.PATROLLING_TIME_PER_LOCATION > 0)
        self.assertTrue(c.MAX_PATROLLING_TIME_PER_VEHICLE > 0)
        self.assertFalse(c.POLICE_STATION in c.PATROL_LOCATIONS)



    def test_create_emergencies(self):
        SIMULATION_DURATION = 60*60*3

        NUMBER_OF_EVENTS_MU = 6
        NUMBER_OF_EVENTS_SIGMA = 4
        TIME_OF_EVENT_MIN = 0
        TIME_OF_EVENT_MAX = SIMULATION_DURATION
        EVENT_DURATION_MU = 60*15
        EVENT_DURATION_SIGMA = 60*5

        POSSIBLE_LOCATIONS_OF_EVENTS = [17322879, 17322882, 17322883, 17322887, 17322888,
                                        17322889, 17322896, 17322899, 27027753, 27027755,
                                        27027758, 27027786, 27027934, 27027935, 27027938,
                                        27027939, 27027940, 27377265, 27377267, 27377268,
                                        29006387, 29006395, 29006403, 29006408, 29006423,
                                        29006424, 29006426, 29006430, 29006478, 29006482]


        for _ in range(100):
            emergencies = mvf.create_emergencies(NUMBER_OF_EVENTS_MU,
                                                 NUMBER_OF_EVENTS_SIGMA,
                                                 TIME_OF_EVENT_MIN,
                                                 TIME_OF_EVENT_MAX,
                                                 EVENT_DURATION_MU,
                                                 EVENT_DURATION_SIGMA,
                                                 POSSIBLE_LOCATIONS_OF_EVENTS)

            # correct indexing
            self.assertTrue( sorted(list(emergencies.keys())) == list(range(0, len(emergencies))) )

            # start time, duration, arrival time, end time, location
            for idx, emergency in emergencies.items():
                self.assertTrue(TIME_OF_EVENT_MIN <= emergency['start_time'] <= TIME_OF_EVENT_MAX)
                self.assertTrue(emergency['duration'] >= 0)
                self.assertTrue(emergency['arrival_time'] is None)
                self.assertTrue(emergency['end_time'] is None)
                self.assertTrue(emergency['assigned_vehicle_id'] is None)
                self.assertTrue(emergency['location'] in POSSIBLE_LOCATIONS_OF_EVENTS)



    def test_create_data_model(self):
        pass



    def test_update_patrol_locations_and_time_windows(self):
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



    def test_VehicleClass_update(self):
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



    def test_VehicleClass_update_current_route(self):
        start = 17322884
        v_id = 1

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



    def test_choose_response_vehicle(self):
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
        result_visited_patrol_locations = [103664213]

        vehicles = [mvf.Vehicle(0, 103664213)]
        vehicles[0].route = [[17322884,   0,      0],
                             [103664213,  35,     215],
                             [293281751,  249,    429],
                             [1829857697, 481,    661]]
        patrol_locations = [103664213, 293281751]
        visited_patrol_locations = []
        current_time = 216
        patrolling_time_per_location = 60*3

        visited_patrol_locations = mvf.update_vpl(visited_patrol_locations,
                                                  patrol_locations,
                                                  vehicles,
                                                  current_time,
                                                  patrolling_time_per_location)

        self.assertTrue(visited_patrol_locations == result_visited_patrol_locations)


if __name__ == '__main__':
    unittest.main()
