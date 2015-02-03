# -*- coding: utf-8 -*-
from collections import namedtuple

Size = namedtuple("Size", ["width", "height"])
Rectangle = namedtuple("Rectangle", ["x0", "y0", "x1", "y1"])

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

class Box(namedtuple("Box", ["point", "size"])):
    __slots__ = ()

    @property
    def rectangle(self):
        return Rectangle(
            x0=self.point.x,
            y0=self.point.y,
            x1=self.point.x+self.size.width,
            y1=self.point.y+self.size.height
        )
