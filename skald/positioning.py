# -*- coding: utf-8 -*-
from collections import namedtuple

from .geometry import Point, Box, Size
from .definitions import Position, Alignment

Choice = namedtuple("Choice", ["point", "punishment"])
Avoid = namedtuple("Avoid", ["rectangle", "punishment"])

def adjust_x_position(choice, size, bounds, margin):
    """Adjusts the position of the box in the horizontal plane to be inside the
    bounds.
    """
    adjust = 0
    if choice.point.x < margin:
        adjust = margin - choice.point.x
    elif choice.point.x+size.width+margin > bounds.width:
        adjust = bounds.width - (choice.point.x + size.width + margin)
    point = Point(x=choice.point.x+adjust, y=choice.point.y)
    return Choice(point=point, punishment=choice.punishment + abs(adjust))

def adjust_y_position(choice, size, bounds, margin):
    """Adjusts the position of the box in the vertical plane to be inside the
    bounds.
    """
    adjust = 0
    if choice.point.y < margin:
        adjust = margin - choice.point.y
    elif choice.point.y+size.height+margin > bounds.height:
        adjust = bounds.height - (choice.point.y + size.height + margin)
    point = Point(x=choice.point.x, y=choice.point.y+adjust)
    return Choice(point=point, punishment=choice.punishment + abs(adjust))

def vertical_align(anchor_box, size, alignment):
    """Finds the vertical position of `box` to be aligned with `anchor_box`
    according to the given `alignment`.
    """
    if alignment == Alignment.top:
        return anchor_box.point.y
    elif alignment == Alignment.bottom:
        return anchor_box.point.y + anchor_box.size.height - size.height
    else:
        vertical_center = anchor_box.point.y + anchor_box.size.height / 2
        return vertical_center - size.height / 2

def horizontal_align(anchor_box, size, alignment):
    """Finds the horizontal position of `box` to be aligned with `anchor_box`
    according to the given `alignment`.
    """
    if alignment == Alignment.left:
        return anchor_box.point.x
    elif alignment == Alignment.right:
        return anchor_box.point.x + anchor_box.size.width - size.width
    else:
        horizontal_center = anchor_box.point.x + anchor_box.size.width / 2
        return horizontal_center - size.width / 2

def get_left_box_position(anchor_box, size, bounds, margin, alignment, avoid):
    x = anchor_box.point.x - size.width - margin
    y = vertical_align(anchor_box, size, alignment)
    point = Point(x, y)

    punishment = 0

    if x < 0:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.left, Alignment.right):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_y_position(choice, size, bounds, margin)

    rect = Box(point=choice.point, size=size).rectangle
    for element in avoid:
        if rect in element.box.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def get_right_box_position(anchor_box, size, bounds, margin, alignment, avoid):
    x = anchor_box.point.x + anchor_box.size.width + margin
    y = vertical_align(anchor_box, size, alignment)
    point = Point(x, y)
    punishment = 0

    if x + size.width > bounds.width:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.left, Alignment.right):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_y_position(choice, size, bounds, margin)

    rect = Box(point=choice.point, size=size).rectangle
    for element in avoid:
        if rect in element.box.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def get_under_box_position(anchor_box, size, bounds, margin, alignment, avoid):
    x = horizontal_align(anchor_box, size, alignment)
    y = anchor_box.point.y + anchor_box.size.height + margin

    point = Point(x, y)
    punishment = 0

    if y + size.height > bounds.height:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.top, Alignment.bottom):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_x_position(choice, size, bounds, margin)

    rect = Box(point=choice.point, size=size).rectangle
    for element in avoid:
        if rect in element.box.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def get_over_box_position(anchor_box, size, bounds, margin, alignment, avoid):
    x = horizontal_align(anchor_box, size, alignment)
    y = anchor_box.point.y - size.height - margin

    point = Point(x, y)
    punishment = 0

    if y < 0:
        return Choice(point=point, punishment=float("inf"))
    if alignment in (Alignment.top, Alignment.bottom):
        return Choice(point=point, punishment=float("inf"))

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_x_position(choice, size, bounds, margin)

    rect = Box(point=choice.point, size=size).rectangle
    for element in avoid:
        if rect in element.box.rectangle:
            choice = Choice(point=choice.point, punishment=float("inf"))
    return choice

def _get_box_position(anchor_box, size, bounds, margin, positions, alignments, avoid):
    """Attempts to find the ideal position of a box of `size` anchored to
    `anchor_box`.

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
            choice = funcs.get(position)(anchor_box, size, bounds, margin, alignment, avoid)
            choices.append(choice)

    choices.sort(key=lambda x: x.punishment)
    choice = choices[0]
    if choice.punishment == float("inf"):
        print("Could not get allowed position for tooltip", tooltip)
    return choice.point

def get_box_position(element, tooltip, size, bounds, margin, avoid):
    positions = tuple(Position)
    if tooltip.positions:
        positions = tooltip.positions
    alignments = tuple(Alignment)
    if tooltip.alignments:
        alignments = tooltip.alignments

    return _get_box_position(
            anchor_box=element.box,
            size=size,
            bounds=bounds,
            margin=margin,
            positions=positions,
            alignments=alignments,
            avoid=avoid)
