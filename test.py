import unittest
import csv

from window import TimeWindow
from input_types import InputFile


class TestTimeWindow(unittest.TestCase):
    def test_width(self):
        self.assertRaises(ValueError, TimeWindow, range(0, 100), width=10, overlap=10)
        self.assertRaises(ValueError, TimeWindow, range(0, 100), width=10, overlap=11)

    def test_length(self):
        window = TimeWindow([(0, i) for i in range(100)], width=6, overlap=2)
        for n in window:
            self.assertEqual(window.width + 1, len(n))

    def test_buffer_size(self):
        # sanity check
        self.assertEqual(TimeWindow([(0, i) for i in range(100)], width=5, overlap=3, iterations=5).size(), 13)  # odd window,  odd overlap
        self.assertEqual(TimeWindow([(0, i) for i in range(100)], width=6, overlap=1, iterations=4).size(), 21)  # even window, odd overlap
        self.assertEqual(TimeWindow([(0, i) for i in range(100)], width=3, overlap=2, iterations=6).size(), 8)  # odd window,  even overlap
        self.assertEqual(TimeWindow([(0, i) for i in range(100)], width=4, overlap=2, iterations=4).size(), 10)  # even window, even overlap

    def test_iterations(self):
        print "iterations"
        window = TimeWindow(width=10, overlap=2, iterations=4)
        window.items = [(0, i) for i in range(window.size())]
        print window.items
        counter = 0
        for i in window:
            counter += 1
        self.assertEqual(window.iterations, counter)


class TestInputFile(unittest.TestCase):
    input_file = InputFile("test/test_data.txt", {"time": "sec", "bp": "CH40", "rr": "CH46"})

    def test_header_finding(self):
        with open("test/test_data.txt") as data_file:
            data_matrix = list(csv.reader(data_file, delimiter=","))
        header_location = TestInputFile.input_file._find_header(data_matrix)
        self.assertEqual(header_location, 33)
        data = data_matrix[header_location + 2:][0]
        self.assertEqual(len(data), 16)

    def test_timestamp_building(self):
        timestamps = TestInputFile.input_file.build_timestamps(["time", "bp", "rr"])
        self.assertEqual(timestamps['bp'][0], (9.0, 0.0))
        self.assertEqual(timestamps['rr'][0], (15.0, 0.0))

if __name__ == '__main__':
    unittest.main()
