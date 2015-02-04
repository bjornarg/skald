# -*- coding: utf-8 -*-
from collections import namedtuple

from .geometry import Point, Box, Size
from .definitions import Position, Alignment

Choice = namedtuple("Choice", ["point", "punishment"])

def adjust_x_position(choice, box, bounds, margin):
    """Adjusts the position of the box in the horizontal plane to be inside the
    bounds.
    """
    adjust = 0
    if choice.point.x < margin:
        adjust = margin - choice.point.x
    elif choice.point.x+box.width+margin > bounds.width:
        adjust = bounds.width - (choice.point.x + box.width + margin)
    point = Point(x=choice.point.x+adjust, y=choice.point.y)
    return Choice(point=point, punishment=choice.punishment + abs(adjust))

def adjust_y_position(choice, box, bounds, margin):
    """Adjusts the position of the box in the vertical plane to be inside the
    bounds.
    """
    adjust = 0
    if choice.point.y < margin:
        adjust = margin - choice.point.y
    elif choice.point.y+box.height+margin > bounds.height:
        adjust = bounds.height - (choice.point.y + box.height + margin)
    point = Point(x=choice.point.x, y=choice.point.y+adjust)
    return Choice(point=point, punishment=choice.punishment + abs(adjust))

def vertical_align(element, box, alignment):
    """Finds the vertical position of `box` to be aligned with `element`
    according to the given `alignment`.
    """
    if alignment == Alignment.top:
        return element.location.y
    elif alignment == Alignment.bottom:
        return element.location.y + element.size.height - box.height
    else:
        vertical_center = element.location.y + element.size.height / 2
        return vertical_center - box.height / 2

def horizontal_align(element, box, alignment):
    """Finds the horizontal position of `box` to be aligned with `element`
    according to the given `alignment`.
    """
    if alignment == Alignment.left:
        return element.location.x
    elif alignment == Alignment.right:
        return element.location.x + element.size.width - box.width
    else:
        horizontal_center = element.location.x + element.size.width / 2
        return horizontal_center - box.width / 2

def get_left_box_position(element, tooltip, box, image_size, margin, alignment):
    x = element.location.x - box.width - margin
    y = vertical_align(element, box, alignment)
    point = Point(x, y)

    punishment = 0

    if x < 0:
        punishment = float("inf")
    if alignment in (Alignment.left, Alignment.right):
        punishment = float("inf")

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_y_position(choice, box, image_size, margin)
    return choice

def get_right_box_position(element, tooltip, box, image_size, margin, alignment):
    x = element.location.x + element.size.width + margin
    y = vertical_align(element, box, alignment)
    point = Point(x, y)
    punishment = 0

    if x + box.width > image_size.width:
        punishment = float("inf")
    if alignment in (Alignment.left, Alignment.right):
        punishment = float("inf")

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_y_position(choice, box, image_size, margin)
    return choice

def get_under_box_position(element, tooltip, box, image_size, margin, alignment):
    x = horizontal_align(element, box, alignment)
    y = element.location.y + element.size.height + margin

    point = Point(x, y)
    punishment = 0

    if y + box.height > image_size.height:
        punishment = float("inf")
    if alignment in (Alignment.top, Alignment.bottom):
        punishment = float("inf")

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_x_position(choice, box, image_size, margin)
    return choice

def get_over_box_position(element, tooltip, box, image_size, margin, alignment):
    x = horizontal_align(element, box, alignment)
    y = element.location.y - box.height - margin

    point = Point(x, y)
    punishment = 0

    if y < 0:
        punishment = float("inf")
    if alignment in (Alignment.top, Alignment.bottom):
        punishment = float("inf")

    choice = Choice(point=point, punishment=punishment)
    choice = adjust_x_position(choice, box, image_size, margin)
    return choice

def get_box_position(element, tooltip, box, image_size, margin):
    funcs = {
        Position.left: get_left_box_position,
        Position.right: get_right_box_position,
        Position.over: get_over_box_position,
        Position.under: get_under_box_position,
    }
    positions = tuple(Position)
    if tooltip.positions:
        positions = tooltip.positions
    alignments = tuple(Alignment)
    if tooltip.alignments:
        alignments = tooltip.alignments

    choices = []

    for position in positions:
        for alignment in alignments:
            choices.append(funcs.get(position)(element, tooltip, box, image_size, margin, alignment))

    choices.sort(key=lambda x: x.punishment)
    choice = choices[0]
    if choice.punishment == float("inf"):
        print("Could not get allowed position for tooltip", tooltip)
    return choice.point
