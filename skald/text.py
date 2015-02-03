# -*- coding: utf-8 -*-
from PIL import ImageFont

from .geometry import Size, Point

from enum import Enum

TextAlign = Enum("TextAlign", "left right center")

class TextArea:
    def __init__(self, wrapper, lines, line_spacing, padding, align):
        self.line_spacing = line_spacing
        self.padding = padding
        self.align = align
        self.lines = lines
        self.wrapper = wrapper

    @classmethod
    def from_lines(cls, lines, font, line_spacing, **kwargs):
        sizes = []
        height = 0
        width = 0
        for line in lines:
            size = Size(*font.getsize(line))
            sizes.append(size)
            width = max(size.width, width)
            height += size.height

        height += (len(lines)-1)*line_spacing

        return cls(
            wrapper=Size(width, height),
            lines=sizes,
            line_spacing=line_spacing,
            **kwargs
        )


    def get_y_offset(self, line_number):
        offset = self.padding
        for i, line in enumerate(self.lines):
            if i >= line_number:
                break
            offset += line.height
        offset += line_number*self.line_spacing
        return offset

    def get_x_offset(self, line_number):
        offset = self.padding
        if self.align == TextAlign.center:
            offset += (self.wrapper.width - self.lines[line_number].width) / 2
        elif self.align == TextAlign.right:
            offset += (self.wrapper.width - self.lines[line_number].width)
        return offset

    def get_offset(self, line_number):
        """Gets the offset for a given line.

        """
        return Point(
            x=self.get_x_offset(line_number),
            y=self.get_y_offset(line_number)
        )

    def get_position(self, start, line_number):
        offset = self.get_offset(line_number)
        return start + offset

    @property
    def width(self):
        return self.wrapper.width + self.padding * 2

    @property
    def height(self):
        return self.wrapper.height + self.padding * 2

    @property
    def size(self):
        return Size(self.width, self.height)
