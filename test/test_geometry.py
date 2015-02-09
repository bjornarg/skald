from unittest import TestCase

from skald.geometry import Size, Box, Point, Rectangle

class TestPoint(TestCase):
    def test_addition(self):
        point1 = Point(x=10, y=50)
        point2 = Point(x=1, y=100)

        added = point1 + point2

        self.assertEqual(added.x, 11)
        self.assertEqual(added.y, 150)

    def test_subtraction(self):
        point1 = Point(x=12, y=150)
        point2 = Point(x=50, y=11)

        subtracted = point1 - point2

        self.assertEqual(subtracted.x, -38)
        self.assertEqual(subtracted.y, 139)
