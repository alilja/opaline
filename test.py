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

if __name__ == '__main__':
    unittest.main()