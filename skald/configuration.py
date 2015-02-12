# -*- coding: utf-8 -*-
import json
import os
from collections import namedtuple

from PIL import ImageFont

Color = namedtuple("Color", ["red", "green", "blue", "alpha"])

def hex_to_tuple(color):
    """Converts a HTML-style RGB(A) hex-string to a
    :py:class:`~skald.configuration.Color`.

    :param color: A hex-string of length 6 or 8, giving RGB values for the
        color. If of length 8, the last two will represent the alpha channel
        of the color. Can optionally be prefixed with a ``#``.
    :return: A :py:class:`~skald.configuration.Color` representation of the
        color.
    """
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
    """Convert ``color`` into type :py:class:`~skald.configuration.Color`.

    :param color: Can either be a HTML-style RGB(A) hex-string, or a 3- or
        4-tuple with (red, green, blue, alpha) values from 0 to 255.
    :param default: The default color to use if ``color`` is ``None``.
    :return: A :py:class:`~skald.configuration.Color` either representing the
        given ``color`` parameter, or simply the ``default``.
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

class Penalties:
    """Penalties are used to calculate how good a tooltip position is.

    """
    def __init__(self, move=1):
        """

        :param move: Used to adjust the penalty when a tooltip needs to be moved
            from it's initially calculated position, such as moving it from
            outside of bounds to the inside. This is multiplied with the number
            of pixels the tooltip is moved.
        """
        self.move = move

class Font:
    """Defines the font to be used when writing text in the documents.
    
    TrueType or OpenType fonts are supported, as long as Pillow is compiled
    with FreeType library support.
    """
    def __init__(self, path=None, size=15, color=None):
        """

        :param path: The path to the TrueType or OpenType font file.
        :param size: Size of the font in points.
        :param color: Color of the text used. See
            :py:func:`~skald.configuration.get_color` for formats colors can be
            given in.
        """
        self.path = path
        self.size = size
        self.color = get_color(color, Color(255, 255, 255, 255))

    def get_font(self):
        """Get a :py:class:`~PIL.ImageFont` instance representing this font."""
        if self.path is None:
            return ImageFont.load_default()
        else:
            return ImageFont.truetype(self.path, self.size)

class Tooltip:
    """Defines style of tooltips."""
    def __init__(self, line_spacing=5, padding=5, margin=10, color=None):
        """

        :param line_spacing: Number of pixels between lines of text.
        :param padding: Number of pixels from text to border of surrounding
            box.
        :param margin: Number of pixels between the tooltip box and the element
            it annotates.
        :param color: Color of the tooltip box. See
            :py:func:`~skald.configuration.get_color` for formats colors can be
            given in.
        """
        self.line_spacing = line_spacing
        self.padding = padding
        self.margin = margin
        self.color = get_color(color, Color(50, 50, 185, 255))

class Configuration:
    def __init__(self, font=None, tooltip=None, penalties=None,
            folder="skald"):
        """Create the base configuration class.

        All ``None`` parameters will be populated with their classes defaults.

        :param font: An instance of :py:class:`~skald.configuration.Font`
            defining the font to be used.
        :param tooltip: An instance of :py:class:`~skald.configuration.Tooltip`
            defining settings for the tooltips.
        :param penalties: An instance of
            :py:class:`~skald.configuration.Penalties` defining how different
            adjustments made to tooltips affect the penalty of the position.
        :param folder: Path to put screenshots, documents and metadata.
        """

        if font is None:
            font = Font()
        self.font = font
        if tooltip is None:
            tooltip = Tooltip()
        self.tooltip = tooltip
        if penalties is None:
            penalties = Penalties()
        self.penalties = penalties
        self.folder = folder

    @classmethod
    def from_dict(cls, dictionary):
        """Creates an instance based on a dictionary.

        Used to create an instance directly from a read configuration file.
        """
        if "font" in dictionary:
            dictionary["font"] = Font(**dictionary.get("font"))
        if "tooltip" in dictionary:
            dictionary["tooltip"] = Tooltip(**dictionary.get("tooltip"))
        if "penalties" in dictionary:
            dictionary["penalties"] = Punishments(**dictionary.get("penalties"))
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
