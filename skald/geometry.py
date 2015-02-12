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
        """Overrides the default ``+`` implementation to sum each element
        in the point.

        Because this is based on :py:obj:`tuple`, the default implementation
        would create a 4-tuple with the elements from both points.
        """
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __sub__(self, other):
        """Implement a subtract function so that each element is subtracted
        from the corresponding element in ``other``.
        """
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)

class Rectangle(namedtuple("Rectangle", ["left", "top", "right", "bottom"])):
    def __contains__(self, other):
        """Check if this rectangle and ``other`` overlaps eachother.

        Essentially this is a bit of a hack to be able to write
        ``rect1 in rect2``.

        :param other: Other rectangle to check if overlaps.
        :return: ``True`` if this rectangle and ``other`` overlaps eachother.
        """
        if self.left < other.right and self.right > other.left and \
                self.top < other.bottom and self.bottom > other.top:
            return True
        return False

    @classmethod
    def from_sizes(cls, size, position):
        """Create a rectangle with a given size and position.

        :param size: The :py:class:`~skald.geometry.Size` of the rectangle.
        :param position: The :py:class:`~skald.geometry.Point` representing
            the position of the rectangle.
        """
        return cls(
            left=position.x,
            top=position.y,
            right=position.x+size.width,
            bottom=position.y+size.height
        )

    def __sub__(self, other):
        """Move the rectangle by subtracting from it's position.

        :param other: A two element :py:obj:`list` or :py:obj:`tuple`, e.g.
            :py:class:`~skald.geometry.Point`.
        """
        if not isinstance(other, (list, tuple)) and len(other) == 2:
            raise TypeError(
                    "Unsupported operand type(s) for -: '%s' and '%s'" % \
                    (type(self).__name__, type(other).__name__)
            )
        return Rectangle(
            left=self.left-other[0],
            top=self.top-other[1],
            right=self.right-other[0],
            bottom=self.bottom-other[1],
        )

    def __add__(self, other):
        """Move the rectangle by adding to it's position.

        :param other: A two element :py:obj:`list` or :py:obj:`tuple`, e.g.
            :py:class:`~skald.geometry.Point`.
        """
        if not isinstance(other, (list, tuple)) and len(other) == 2:
            raise TypeError(
                    "Unsupported operand type(s) for +: '%s' and '%s'" % \
                    (type(self).__name__, type(other).__name__)
            )
        return Rectangle(
            left=self.left+other[0],
            top=self.top+other[1],
            right=self.right+other[0],
            bottom=self.bottom+other[1],
        )

    @property
    def center(self):
        """The :py:class:`~skald.geometry.Point` at the center of the
        rectangle.
        """
        return Point(x=(self.left+self.right)/2, y=(self.top+self.bottom)/2)

    @property
    def size(self):
        """The :py:class:`~skald.geometry.Size` of the rectangle."""
        return Size(width=self.width, height=self.height)

    @property
    def position(self):
        """The :py:class:`~skald.geometry.Point` for the top left position
        of the rectangle.
        """
        return Point(x=self.left, y=self.top)

    @property
    def height(self):
        return self.bottom-self.top

    @property
    def width(self):
        return self.right-self.left

    @property
    def box(self):
        """The :py:class:`~skald.geometry.Box` representation of itself."""
        return Box(
            point=self.position,
            size=self.size
        )
