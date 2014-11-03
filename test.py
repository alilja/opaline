import unittest

from opaline.window import Window

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


if __name__ == '__main__':
    unittest.main()