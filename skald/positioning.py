# -*- coding: utf-8 -*-
from collections import namedtuple

from .geometry import Point, Size, Rectangle
from .definitions import Position, Alignment

Choice = namedtuple("Choice", ["point", "score"])
Avoid = namedtuple("Avoid", ["rectangle", "score"])

def adjust_x_position(choice, size, bounds, margin, score):
    """Adjusts the position of the box in the horizontal plane to be inside the
    bounds.

    :param choice: The choice to adjust position for.
    :param size: Size of the element being positioned.
    :param bounds: Bounds the element has to be within.
    :param margin: The margin the element has to have from the bounds.
    :param score: The score it costs to move the element per pixel.
    """
    adjust = 0
    if choice.point.x < margin:
        adjust = margin - choice.point.x
    elif choice.point.x+size.width+margin > bounds.width:
        adjust = bounds.width - (choice.point.x + size.width + margin)
    point = Point(x=choice.point.x+adjust, y=choice.point.y)
    return Choice(point=point, score=choice.score + abs(adjust) * score)

def adjust_y_position(choice, size, bounds, margin, score):
    """Adjusts the position of the box in the vertical plane to be inside the
    bounds.

    :param choice: The choice to adjust position for.
    :param size: Size of the element being positioned.
    :param bounds: Bounds the element has to be within.
    :param margin: The margin the element has to have from the bounds.
    :param score: The score it costs to move the element per pixel.
    """
    adjust = 0
    if choice.point.y < margin:
        adjust = margin - choice.point.y
    elif choice.point.y+size.height+margin > bounds.height:
        adjust = bounds.height - (choice.point.y + size.height + margin)
    point = Point(x=choice.point.x, y=choice.point.y+adjust)
    return Choice(point=point, score=choice.score + abs(adjust) * score)

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
        scores):
    x = anchor.x0 - size.width - margin
    y = vertical_align(anchor, size, alignment)
    point = Point(x, y)

    score = 0

    if x < 0:
        return Choice(point=point, score=float("inf"))
    if alignment in (Alignment.left, Alignment.right):
        return Choice(point=point, score=float("inf"))

    choice = Choice(point=point, score=score)
    choice = adjust_y_position(choice, size, bounds, margin, scores.move)

    rect = Rectangle.from_sizes(position=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, score=float("inf"))
    return choice

def get_right_box_position(anchor, size, bounds, margin, alignment, avoid,
        scores):
    x = anchor.x1 + margin
    y = vertical_align(anchor, size, alignment)
    point = Point(x, y)
    score = 0

    if x + size.width > bounds.width:
        return Choice(point=point, score=float("inf"))
    if alignment in (Alignment.left, Alignment.right):
        return Choice(point=point, score=float("inf"))

    choice = Choice(point=point, score=score)
    choice = adjust_y_position(choice, size, bounds, margin, scores.move)

    rect = Rectangle.from_sizes(position=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, score=float("inf"))
    return choice

def get_under_box_position(anchor, size, bounds, margin, alignment, avoid,
        scores):
    x = horizontal_align(anchor, size, alignment)
    y = anchor.y1 + margin

    point = Point(x, y)
    score = 0

    if y + size.height > bounds.height:
        return Choice(point=point, score=float("inf"))
    if alignment in (Alignment.top, Alignment.bottom):
        return Choice(point=point, score=float("inf"))

    choice = Choice(point=point, score=score)
    choice = adjust_x_position(choice, size, bounds, margin, scores.move)

    rect = Rectangle.from_sizes(position=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, score=float("inf"))
    return choice

def get_over_box_position(anchor, size, bounds, margin, alignment, avoid,
        scores):
    x = horizontal_align(anchor, size, alignment)
    y = anchor.y0 - size.height - margin

    point = Point(x, y)
    score = 0

    if y < 0:
        return Choice(point=point, score=float("inf"))
    if alignment in (Alignment.top, Alignment.bottom):
        return Choice(point=point, score=float("inf"))

    choice = Choice(point=point, score=score)
    choice = adjust_x_position(choice, size, bounds, margin, scores.move)

    rect = Rectangle.from_sizes(position=choice.point, size=size)
    for element in avoid:
        if rect in element.rectangle:
            choice = Choice(point=choice.point, score=float("inf"))
    return choice

def _get_box_position(anchor, size, bounds, margin, positions, alignments,
        avoid, scores):
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
                    avoid=avoid, scores=scores)
            choices.append(choice)

    choices.sort(key=lambda x: x.score)
    return choices

def get_box_position(element, tooltip, size, bounds, margin, avoid, scores):
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
            scores=scores)
