# -*- coding: utf-8 -*-
from enum import Enum

from PIL import ImageFont

from .geometry import Size, Point, Rectangle, Box

TextAlign = Enum("TextAlign", "left right center")

class TextArea:
    def __init__(self, text, wrapper, line_sizes, line_spacing, padding, align):
        self.line_spacing = line_spacing
        self.padding = padding
        self.align = align
        self.line_sizes = line_sizes
        self.text = text
        self.wrapper = wrapper
        self.position = Point(0, 0)
        self.choices = []

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
            text=lines,
            line_sizes=sizes,
            line_spacing=line_spacing,
            **kwargs
        )

    def _get_y_offset(self, line_number):
        offset = self.padding
        for i, line in enumerate(self.line_sizes):
            if i >= line_number:
                break
            offset += line.height
        offset += line_number*self.line_spacing
        return offset

    def _get_x_offset(self, line_number):
        offset = self.padding
        if self.align == TextAlign.center:
            offset += (self.wrapper.width - self.line_sizes[line_number].width) / 2
        elif self.align == TextAlign.right:
            offset += (self.wrapper.width - self.line_sizes[line_number].width)
        return offset

    def get_line_offset(self, line_number):
        """Gets the internal offset of a given line relative to the textarea"""
        return Point(
            x=self._get_x_offset(line_number),
            y=self._get_y_offset(line_number)
        )

    def get_line_position(self, line_number):
        """Gets the absolute position of the given line number"""
        offset = self.get_line_offset(line_number)
        return self.position + offset

    @property
    def width(self):
        return self.wrapper.width + self.padding * 2

    @property
    def height(self):
        return self.wrapper.height + self.padding * 2

    @property
    def size(self):
        return Size(self.width, self.height)

    @property
    def box(self):
        return self.rectangle.box

    @property
    def rectangle(self):
        return Rectangle.from_sizes(size=self.size, position=self.position)
