# -*- coding: utf-8 -*-
from collections import namedtuple

Size = namedtuple("Size", ["width", "height"])
Box = namedtuple("Box", ["point", "size"])

class Point(namedtuple("Point", ["x", "y"])):
    """Point in a two-dimensional space.

    Named tuple implementation that allows for addition and subtraction.
    """
    __slots__ = ()

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)

class Rectangle(namedtuple("Rectangle", ["x0", "y0", "x1", "y1"])):
    def __contains__(self, other):
        """Check if this rectangle and `other` overlaps eachother.

        Essentially this is a bit of a hack to be able to write
        `rect1 in rect2`.
        """
        if self.x0 < other.x1 and self.x1 > other.x0 and \
                self.y0 < other.y1 and self.y1 > other.y0:
            return True
        return False

    @classmethod
    def from_sizes(cls, size, point):
        return cls(
            x0=point.x,
            y0=point.y,
            x1=point.x+size.width,
            y1=point.y+size.height
        )

    @property
    def center(self):
        """Returns the point in the center of the rectangle."""
        return Point(x=(self.x0+self.x1)/2, y=(self.y0+self.y1)/2)

    @property
    def box(self):
        return Box(
            point=Point(x=self.x0, y=self.y0),
            size=Size(width=self.x1-self.x0, height=self.y1-self.y0)
        )
