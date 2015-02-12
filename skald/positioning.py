# -*- coding: utf-8 -*-
from collections import namedtuple

from .geometry import Point, Size, Rectangle
from .definitions import Position, Alignment

Choice = namedtuple("Choice", ["rectangle", "penalty"])
Avoid = namedtuple("Avoid", ["rectangle", "penalty"])
Adjustment = namedtuple("Adjustment", ["point", "penalty"])

def adjust_x_position(rectangle, bounds, margin):
    """Find the horizontal adjustment necessary to keep a rectangle within
    the bounds.

    :param rectangle: The choice to adjust position for.
    :param bounds: Bounds the element has to be within.
    :param margin: The margin the element has to have from the bounds.
    """
    adjust = 0
    if rectangle.left < margin:
        adjust = margin - rectangle.left
    elif rectangle.right+margin > bounds.width:
        adjust = bounds.width - (rectangle.right + margin)

    return Point(x=adjust, y=0)

def adjust_y_position(rectangle, bounds, margin):
    """Find the vertical adjustment necessary to keep a rectangle within
    bounds.

    :param rectangle: The choice to adjust position for.
    :param bounds: Bounds the element has to be within.
    :param margin: The margin the element has to have from the bounds.
    """
    adjust = 0
    if rectangle.top < margin:
        adjust = margin - rectangle.top
    elif rectangle.bottom+margin > bounds.height:
        adjust = bounds.height - (rectangle.bottom + margin)

    return Point(x=0, y=adjust)

def vertical_align(anchor, size, alignment):
    """Finds the vertical position of `box` to be aligned with `anchor`
    according to the given `alignment`.
    """
    if alignment == Alignment.top:
        return anchor.top
    elif alignment == Alignment.bottom:
        return anchor.bottom - size.height
    else:
        return anchor.center.y - size.height / 2

def horizontal_align(anchor, size, alignment):
    """Finds the horizontal position of `box` to be aligned with `anchor`
    according to the given `alignment`.
    """
    if alignment == Alignment.left:
        return anchor.left
    elif alignment == Alignment.right:
        return anchor.right - size.width
    else:
        return anchor.center.x - size.width / 2

def align_over_position(anchor, size, alignment, margin):
    """Find the position of a rectangle over a given anchor.

    :param anchor: A :py:class:`~skald.geometry.Rectangle` to anchor the
        rectangle to.
    :param size: The :py:class:`~skald.geometry.Size` of the rectangle.
    :param alignment: The :py:class:`~skald.definitions.Alignment` of the
        rectangle.
    :param margin: The margin, in pixels, the rectangle must have from the
        anchor.
    """
    x = horizontal_align(anchor, size, alignment)
    y = anchor.top - size.height - margin
    return Point(x=x, y=y)
def align_under_position(anchor, size, alignment, margin):
    """Find the position of a rectangle under a given anchor.

    :param anchor: A :py:class:`~skald.geometry.Rectangle` to anchor the
        rectangle to.
    :param size: The :py:class:`~skald.geometry.Size` of the rectangle.
    :param alignment: The :py:class:`~skald.definitions.Alignment` of the
        rectangle.
    :param margin: The margin, in pixels, the rectangle must have from the
        anchor.
    """
    x = horizontal_align(anchor, size, alignment)
    y = anchor.bottom + margin
    return Point(x=x, y=y)
def align_right_position(anchor, size, alignment, margin):
    """Find the position of a rectangle to the right of a given anchor.

    :param anchor: A :py:class:`~skald.geometry.Rectangle` to anchor the
        rectangle to.
    :param size: The :py:class:`~skald.geometry.Size` of the rectangle.
    :param alignment: The :py:class:`~skald.definitions.Alignment` of the
        rectangle.
    :param margin: The margin, in pixels, the rectangle must have from the
        anchor.
    """
    x = anchor.right + margin
    y = vertical_align(anchor, size, alignment)
    return Point(x=x, y=y)
def align_left_position(anchor, size, alignment, margin):
    """Find the position of a rectangle to the left of a given anchor.

    :param anchor: A :py:class:`~skald.geometry.Rectangle` to anchor the
        rectangle to.
    :param size: The :py:class:`~skald.geometry.Size` of the rectangle.
    :param alignment: The :py:class:`~skald.definitions.Alignment` of the
        rectangle.
    :param margin: The margin, in pixels, the rectangle must have from the
        anchor.
    """
    x = anchor.left - size.width - margin
    y = vertical_align(anchor, size, alignment)
    return Point(x=x, y=y)

def _init_box_position(anchor, size, bounds, margin, position, alignment,
        avoid, penalties):
    allowed_alignments = {
        Position.left: (Alignment.top, Alignment.bottom, Alignment.center),
        Position.right: (Alignment.top, Alignment.bottom, Alignment.center),
        Position.over: (Alignment.left, Alignment.right, Alignment.center),
        Position.under: (Alignment.left, Alignment.right, Alignment.center),
    }

    if alignment not in allowed_alignments[position]:
        return None

    align_positions = {
        Position.left: align_left_position,
        Position.right: align_right_position,
        Position.over: align_over_position,
        Position.under: align_under_position,
    }

    point = align_positions[position](anchor, size, alignment, margin)
    rectangle = Rectangle.from_sizes(size=size, position=point)

    adjust_positions = {
        Position.left: adjust_y_position,
        Position.right: adjust_y_position,
        Position.over: adjust_x_position,
        Position.under: adjust_x_position,
    }

    adjustment = adjust_positions[position](rectangle, bounds, margin)
    rectangle = rectangle + adjustment
    penalty = sum([abs(p) for p in adjustment]) * penalties.move

    for element in avoid:
        if rectangle in element.rectangle:
            return None
    return Choice(rectangle=rectangle, penalty=penalty)

def get_box_position(element, tooltip, size, bounds, margin, avoid, penalties):
    positions = tuple(Position)
    if tooltip.positions:
        positions = tooltip.positions
    alignments = tuple(Alignment)
    if tooltip.alignments:
        alignments = tooltip.alignments

    choices = []
    for position in positions:
        for alignment in alignments:
            choice = _init_box_position(anchor=element.rectangle, size=size,
                    bounds=bounds, margin=margin, alignment=alignment,
                    avoid=avoid, penalties=penalties, position=position)
            if choice is not None:
                choices.append(choice)

    choices.sort(key=lambda x: x.penalty)
    return choices
