from unittest import TestCase
from skald.positioning import adjust_x_position, adjust_y_position, Choice
from skald.geometry import Size, Point

class TestAdjustXPosition(TestCase):
    def test_moves_from_lower_bounds(self):
        initial_choice = Choice(point=Point(x=-5, y=0), score=0)
        margin = 10
        bounds = Size(width=100, height=100)
        size = Size(width=10, height=10)
        choice = adjust_x_position(initial_choice, size, bounds, margin, 1)
        self.assertEqual(choice.point.x, 10)
        self.assertEqual(choice.score, 15)

    def test_moves_from_upper_bounds(self):
        initial_choice = Choice(point=Point(x=150, y=0), score=0)
        margin = 10
        bounds = Size(width=100, height=100)
        size = Size(width=10, height=10)
        choice = adjust_x_position(initial_choice, size, bounds, margin, 1)
        self.assertEqual(choice.point.x, 80)
        self.assertEqual(choice.score, 70)

class TestAdjustYPosition(TestCase):
    def test_moves_from_lower_bounds(self):
        initial_choice = Choice(point=Point(x=-5, y=0), score=0)
        margin = 10
        bounds = Size(width=100, height=100)
        size = Size(width=10, height=10)
        choice = adjust_y_position(initial_choice, size, bounds, margin, 1)
        self.assertEqual(choice.point.y, 10)
        self.assertEqual(choice.score, 10)

    def test_moves_from_upper_bounds(self):
        initial_choice = Choice(point=Point(x=-5, y=100), score=0)
        margin = 10
        bounds = Size(width=100, height=100)
        size = Size(width=10, height=20)
        choice = adjust_y_position(initial_choice, size, bounds, margin, 0.1)
        self.assertEqual(choice.point.y, 70)
        self.assertEqual(choice.score, 3)
