# -*- coding: utf-8 -*-
import json
import os
from collections import namedtuple

from PIL import ImageFont

Color = namedtuple("Color", ["red", "green", "blue", "alpha"])

def hex_to_tuple(color):
    """Converts a HTML-style RGB(A) hex-string to a `Color`."""
    if color.startswith("#"):
        color = color[1:]
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    if len(color) == 8:
        alpha = int(color[6:8], 16)
    else:
        alpha = 255
    return Color(red, green, blue, alpha)

def get_color(color, default):
    """Convert `color` into type `Color`.

    `color` can either be a HTML-style RGB(A) hex-string, or a 3- or 4-tuple
    with (red, green, blue, alpha) values from 0 to 255.
    """
    if color is None:
        return default
    elif isinstance(color, basestring):
        return hex_to_tuple(color)
    else:
        if len(color) == 3:
            return Color(*color, alpha=255)
        else:
            return Color(*color)

class Punishments:
    def __init__(self, move=1):
        self.move = move

class Font:
    """Defines a font."""
    def __init__(self, path=None, size=15, color=None):
        self.path = path
        self.size = size
        self.color = get_color(color, Color(255, 255, 255, 255))

    def get_font(self):
        """Get a Pillow `ImageFont` instance representing this font.

        If no `path` is specified, the default Pillow font is used.
        """
        if self.path is None:
            return ImageFont.load_default()
        else:
            return ImageFont.truetype(self.path, self.size)

class Tooltip:
    """Defines style of tooltips."""
    def __init__(self, line_spacing=5, padding=5, margin=10, color=None):
        self.line_spacing = line_spacing
        self.padding = padding
        self.margin = margin
        self.color = get_color(color, Color(50, 50, 185, 255))

class Configuration:
    def __init__(self, font=None, tooltip=None, punishments=None,
            input="skald", output="skald"):

        if font is None:
            font = Font()
        self.font = font
        if tooltip is None:
            tooltip = Tooltip()
        self.tooltip = tooltip
        if punishments is None:
            punishments = Punishments()
        self.punishments = punishments
        self.input = input
        self.output = output

    @classmethod
    def from_dict(cls, dictionary):
        if "font" in dictionary:
            dictionary["font"] = Font(**dictionary.get("font"))
        if "tooltip" in dictionary:
            dictionary["tooltip"] = Tooltip(**dictionary.get("tooltip"))
        if "punishments" in dictionary:
            dictionary["punishments"] = Punishments(**dictionary.get("punishments"))
        return cls(**dictionary)

def read_configuration(path=None):
    """Reads skald configuration.

    `path` can either be a directory containing a `skald.json` file, or a
    direct path to a configuration file. If `path` is unspecified, it will
    look for a `skald.json` inside the execution directory.

    If a configuration file is found, it will be used to update
    `DEFAULT_CONFIG`.

    """
    if path is None:
        path = os.getcwd()

    if os.path.isdir(path):
        path = os.path.join(path, "skald.json")

    if os.path.exists(path):
        with open(path, "r") as config_file:
            read_config = json.load(config_file)
            return Configuration.from_dict(read_config)

    return Configuration()
