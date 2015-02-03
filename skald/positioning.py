# -*- coding: utf-8 -*-
from collections import namedtuple

from .geometry import Point, Box, Size
from .definitions import Position, Alignment

Choice = namedtuple("Choice", ["point", "punishment"])

def get_left_box_position(element, tooltip, box, margin):
    vertical_center = element.location.y + element.size.height / 2
    x = element.location.x - box.width - margin
    y = vertical_center - box.height / 2
    return Point(x, y)

def get_right_box_position(element, tooltip, box, margin):
    vertical_center = element.location.y + element.size.height / 2
    x = element.location.x + element.size.width + margin
    y = vertical_center - box.height / 2
    return Point(x, y)

def get_under_box_position(element, tooltip, box, margin):
    horizontal_center = element.location.x + element.size.width / 2
    x = horizontal_center - box.width / 2
    y = element.location.y + element.size.height + margin
    return Point(x, y)

def get_over_box_position(element, tooltip, box, margin):
    horizontal_center = element.location.x + element.size.width / 2
    x = horizontal_center - box.width / 2
    y = element.location.y - box.height - margin
    return Point(x, y)

def get_box_position(element, tooltip, box, margin):
    positions = {
        Position.left: get_left_box_position,
        Position.right: get_right_box_position,
        Position.over: get_over_box_position,
        Position.under: get_under_box_position,
    }
    choices = tuple(Position)
    if tooltip.positions:
        choices = tooltip.positions
    for choice in choices:
        func = positions.get(choice)
        return func(element, tooltip, box, margin)
