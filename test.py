import unittest

from window import Window
from input_types import InputFile

class TestWindow(unittest.TestCase):
    def test_width(self):
        self.assertRaises(ValueError, Window, range(0,100), width=10, overlap=10)
        self.assertRaises(ValueError, Window, range(0,100), width=10, overlap=11)

    def test_length(self):
        window = Window(range(0,100), width=5, overlap=3)
        for n in window:
            self.assertEqual(window.width, len(n))

    def test_buffer_size(self):
        # sanity check
        self.assertEqual(len(Window(range(0,100), width=5, overlap=3, iterations=5)), 13) # odd window,  odd overlap
        self.assertEqual(len(Window(range(0,100), width=6, overlap=1, iterations=4)), 21) # even window, odd overlap
        self.assertEqual(len(Window(range(0,100), width=3, overlap=2, iterations=6)), 8)  # odd window,  even overlap
        self.assertEqual(len(Window(range(0,100), width=4, overlap=2, iterations=4)), 10) # even window, even overlap

    def test_list_of_tuples(self):
        a = [
            (0, 1, 2),
            (2, 3, 4),
            (4, 5, 6),
            (6, 7, 8),
            (8, 9, 10),
            (10, 11, 12),
            (12, 13, 14),
            (14, 15, 16),
            (16, 17, 18),
            (18, 19, 20),
            (20, 21, 22),
            (22, 23, 24),
            (24, 25, 26),
            (26, 27, 28),
            (28, 29, 30),
            (30, 31, 32),
            (32, 33, 34),
            (34, 35, 36),
            (36, 37, 38),
            (38, 39, 40),
            (40, 41, 42),
            (42, 43, 44),
            (44, 45, 46),
            (46, 47, 48),
            (48, 49, 50),
            (50, 51, 52),
            (52, 53, 54),
            (54, 55, 56),
            (56, 57, 58),
            (58, 59, 60),
            ]

        window = Window(a, width=3, overlap=2)

        # finish me with __getitem__ in window function

class TestInputFile(unittest.TestCase):
    def test_processing(self):
        input_file = InputFile("test/test_data.txt",{"sec":"time", "CH40":"bp", "CH46":"rr"})
        self.assertEqual(len(input_file.data[0]),16)
        self.assertEqual(len(input_file.channel_data["time"]),1)
        self.assertEqual(input_file.channel_data["time"][0],0)

if __name__ == '__main__':
    unittest.main()