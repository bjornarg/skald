# -*- coding: utf-8 -*-
from collections import namedtuple

from .geometry import Point, Size, Rectangle
from .definitions import Position, Alignment

Choice = namedtuple("Choice", ["point", "punishment"])
Avoid = namedtuple("Avoid", ["rectangle", "punishment"])

def adjust_x_position(choice, size, bounds, margin, punishment):
    """Adjusts the position of the box in the horizontal plane to be inside the
    bounds.
    """
    adjust = 0
    if choice.point.x < margin:
        adjust = margin - choice.point.x
    elif choice.point.x+size.width+margin > bounds.width:
        adjust = bounds.width - (choice.point.x + size.width + margin)
    point = Point(x=choice.point.x+adjust, y=choice.point.y)
    return Choice(point=point, punishment=choice.punishment + abs(adjust) * punishment)

def adjust_y_position(choice, size, bounds, margin, punishment):
    """Adjusts the position of the box in the vertical plane to be inside the
    bounds.
    """
    adjust = 0
    if choice.point.y < margin:
        adjust = margin - choice.point.y
    elif choice.point.y+size.height+margin > bounds.height:
        adjust = bounds.height - (choice.point.y + size.height + margin)
    point = Point(x=choice.point.x, y=choice.point.y+adjust)
    return Choice(point=point, punishment=choice.punishment + abs(adjust) * punishment)

def vertical_align(anchor, size, alignment):
    """Finds the vertical position of `box` to be aligned with `anchor`
    according to the given `alignment`.
    """
    if alignment == Alignment.top:
        return anchor.y0
    elif alignment == Alignment.bottom:
        return anchor.y1 - size.height
    else:
        return anchor.center.y - size.height / 2

def horizontal_align(anchor, size, alignment):
    """Finds the horizontal position of `box` to be aligned with `anchor`
    according to the given `alignment`.
    """
    if alignment == Alignment.left:
        return anchor.x0
    elif alignment == Alignment.right:
        return anchor.x1 - size.width
    else:
        return anchor.center.x - size.width / 2

def get_left_box_position(anchor, size, bounds, margin, alignment, avoid,
        punishments):
    x = anchor.x0 - size.width - margin
    y = vertical_align(anchor, size, alignment)
    point = Point(x, y)

    punishment = 0

    if x < 0:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.left, Alignment.right):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_y_position(choice, size, bounds, margin, punishments)

    rect = Rectangle.from_sizes(point=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def get_right_box_position(anchor, size, bounds, margin, alignment, avoid,
        punishments):
    x = anchor.x1 + margin
    y = vertical_align(anchor, size, alignment)
    point = Point(x, y)
    punishment = 0

    if x + size.width > bounds.width:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.left, Alignment.right):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_y_position(choice, size, bounds, margin, punishments)

    rect = Rectangle.from_sizes(point=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def get_under_box_position(anchor, size, bounds, margin, alignment, avoid,
        punishments):
    x = horizontal_align(anchor, size, alignment)
    y = anchor.y1 + margin

    point = Point(x, y)
    punishment = 0

    if y + size.height > bounds.height:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.top, Alignment.bottom):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_x_position(choice, size, bounds, margin, punishments.move)

    rect = Rectangle.from_sizes(point=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def get_over_box_position(anchor, size, bounds, margin, alignment, avoid,
        punishments):
    x = horizontal_align(anchor, size, alignment)
    y = anchor.y0 - size.height - margin

    point = Point(x, y)
    punishment = 0

    if y < 0:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.top, Alignment.bottom):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_x_position(choice, size, bounds, margin, punishments.move)

    rect = Rectangle.from_sizes(point=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def _get_box_position(anchor, size, bounds, margin, positions, alignments,
        avoid, punishments):
    """Attempts to find the ideal position of a box of `size` anchored to
    `anchor`.

    """
    funcs = {
        Position.left: get_left_box_position,
        Position.right: get_right_box_position,
        Position.over: get_over_box_position,
        Position.under: get_under_box_position,
    }
    choices = []
    for position in positions:
        for alignment in alignments:
            choice = funcs.get(position)(anchor=anchor, size=size,
                    bounds=bounds, margin=margin, alignment=alignment,
                    avoid=avoid, punishments=punishments)
            choices.append(choice)

    choices.sort(key=lambda x: x.punishment)
    return choices

def get_box_position(element, tooltip, size, bounds, margin, avoid, punishments):
    positions = tuple(Position)
    if tooltip.positions:
        positions = tooltip.positions
    alignments = tuple(Alignment)
    if tooltip.alignments:
        alignments = tooltip.alignments

    return _get_box_position(
            anchor=element.rectangle,
            size=size,
            bounds=bounds,
            margin=margin,
            positions=positions,
            alignments=alignments,
            avoid=avoid,
            punishments=punishments)
