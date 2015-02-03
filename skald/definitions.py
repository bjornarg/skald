# -*- coding: utf-8 -*-
import os
import json
import re
from enum import Enum

from .geometry import Size, Point, Box

Position = Enum("Position", "over under left right")
Alignment = Enum("Alignment", "top bottom left right center")

def get_positions(positions):
    if positions is None:
        return []
    ret = []
    if isinstance(positions, str):
        positions = re.split(r"\s", positions)
    for position in positions:
        ret.append(Position[position.lower()])
    return ret

def get_alignments(alignments):
    if alignments is None:
        return []
    ret = []
    if isinstance(alignments, str):
        alignments = re.split(r"\s", alignments)
    for alignment in alignments:
        ret.append(Alignment[alignment.lower()])
    return ret

class Tooltip:
    """A tooltip connected to a element."""
    def __init__(self, lines, positions=None, alignments=None, force=False,
            width=None):
        self.lines = lines
        self.width = width
        self.positions = get_positions(positions)
        self.alignments = get_alignments(alignments)
        self.force = force

class Element:
    """Represents a element on the page."""
    def __init__(self, element=None, location=None, size=None,
            allow_overwrite=False):
        if element is not None:
            self.location = Point(x=element.location["x"], y=element.location["y"])
            self.size = Size(width=element.size["width"], height=element.size["height"])
        else:
            self.location = location
            self.size = size
        self.allow_overwrite = allow_overwrite
        self.tooltips = []

    def add_tooltip(self, *tooltips):
        self.tooltips.extend(tooltips)

    @property
    def box(self):
        return Box(size=self.size, point=self.location)

class Document:
    """A document that documents elements in a screenshot."""
    def __init__(self, name):
        self.name = name
        self.elements = []

    def add_element(self, *elements):
        self.elements.extend(elements)

class Screenshot:
    """A single screenshot.

    A screenshot can contain multiple documents, which will each use the same
    screenshot as it's base.

    """
    def __init__(self, name, path):
        self.name = name
        self.documents = []
        self.path = path

    def add_document(self, document):
        self.documents.append(document)

    @property
    def image_path(self):
        return os.path.join(self.path, "%s.png" % self.name)

    @property
    def meta_path(self):
        return os.path.join(self.path, "%s.json" % self.name)

class ScreenshotEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Screenshot):
            return {
                "name": obj.name,
                "path": obj.path,
                "documents": [self.default(document) for document in obj.documents],
            }
        elif isinstance(obj, Document):
            return {
                "name": obj.name,
                "elements": [self.default(element) for element in obj.elements],
            }
        elif isinstance(obj, Element):
            return {
                "location": obj.location,
                "size": obj.size,
                "allow_overwrite": obj.allow_overwrite,
                "tooltips": [self.default(tooltip) for tooltip in obj.tooltips],
            }
        elif isinstance(obj, Tooltip):
            return {
                "lines": obj.lines,
                "width": obj.width,
                "positions": obj.positions,
                "alignments": obj.alignments,
                "force": obj.force
            }
        elif isinstance(obj, Position):
            return obj.name
        return super().default(obj)

class ScreenshotDecoder(json.JSONDecoder):
    """Decodes a JSON string as a `Screenshot` object."""
    def decode(self, string):
        obj = super().decode(string)
        screenshot = Screenshot(obj["name"], obj["path"])
        screenshot.add_document(*self.get_documents(obj["documents"]))
        return screenshot

    def get_documents(self, documents):
        ret = []
        for document in documents:
            obj = Document(document["name"])
            obj.add_element(*self.get_elements(document["elements"]))
            ret.append(obj)
        return ret

    def get_elements(self, elements):
        ret = []
        for element in elements:
            location = Point(*element["location"])
            size = Size(*element["size"])
            allow_overwrite = element.get("allow_overwrite", False)
            obj = Element(
                location=location,
                size=size,
                allow_overwrite=allow_overwrite
            )
            obj.add_tooltip(*self.get_tooltips(element["tooltips"]))
            ret.append(obj)
        return ret

    def get_tooltips(self, tooltips):
        ret = []
        for tooltip in tooltips:
            obj = Tooltip(
                lines=tooltip["lines"],
                positions=tooltip["positions"],
                alignments=tooltip["alignments"],
                force=tooltip.get("force", False),
                width=tooltip.get("width", None),
            )
            ret.append(obj)
        return ret

def save(screenshot, driver):
    if not os.path.exists(screenshot.path):
        os.mkdir(screenshot.path)

    driver.save_screenshot(screenshot.image_path)
    with open(screenshot.meta_path, "w") as json_file:
        json.dump(screenshot, json_file, cls=ScreenshotEncoder)

def load(path):
    with open(path, "r") as json_file:
        return json.load(json_file, cls=ScreenshotDecoder)
