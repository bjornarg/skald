from unittest import TestCase
from skald.positioning import adjust_x_position, adjust_y_position, Choice
from skald.geometry import Size, Rectangle

class TestAdjustXPosition(TestCase):
    def test_moves_from_lower_bounds(self):
        rectangle = Rectangle(left=-5, top=0, right=100, bottom=100)
        margin = 10
        bounds = Size(width=100, height=100)
        point = adjust_x_position(rectangle, bounds, margin)
        self.assertEqual(point.x, 15)
        self.assertEqual(point.y, 0)

    def test_moves_from_upper_bounds(self):
        rectangle = Rectangle(left=150, top=0, right=160, bottom=100)
        margin = 10
        bounds = Size(width=100, height=100)
        point = adjust_x_position(rectangle, bounds, margin)
        self.assertEqual(point.x, -70)
        self.assertEqual(point.y, 0)

class TestAdjustYPosition(TestCase):
    def test_moves_from_lower_bounds(self):
        rectangle = Rectangle(left=0, top=0, right=160, bottom=100)
        margin = 10
        bounds = Size(width=100, height=100)
        point = adjust_y_position(rectangle, bounds, margin)
        self.assertEqual(point.x, 0)
        self.assertEqual(point.y, 10)

    def test_moves_from_upper_bounds(self):
        rectangle = Rectangle(left=0, top=150, right=160, bottom=200)
        margin = 10
        bounds = Size(width=100, height=100)
        point = adjust_y_position(rectangle, bounds, margin)
        self.assertEqual(point.x, 0)
        self.assertEqual(point.y, -110)
