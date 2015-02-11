# -*- coding: utf-8 -*-
import os
import json
import re
from enum import Enum

from .geometry import Size, Point, Rectangle

Position = Enum("Position", "left over right under")
Alignment = Enum("Alignment", "center top bottom left right")

def get_positions(positions):
    """Converts positions from string representation to enum.

    :param positions: Either a list or a space-separated string of positions.
    :return: A list of :py:class:`~skald.definitions.Position` corresponding to
        the given ``positions``.
    """
    if positions is None:
        return []
    ret = []
    if isinstance(positions, str):
        positions = re.split(r"\s", positions)
    for position in positions:
        ret.append(Position[position.lower()])
    return ret

def get_alignments(alignments):
    """Convers alignments from string representation to enum.

    :param alignments: Either a list or a space-separated string of alignments.
    :return: A list of :py:class:`~skald.definitions.Alignment` corresponding
        to the given ``alignments``.
    """
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
        """

        :param lines: If a string, it will be split on newlines (``\\n``) to
            create a list. Can also be an already split. Each represents a
            single line in the tooltip text.
        :param positions: Defines possible positions around the element this
            tooltip is allowed to have.
            See :py:func:`~skald.definitions.get_positions` for how this
            argument is parsed.
        :param alignments: Defines possible alignments with reference to the
            element this tooltip is allowed to have.
            See :py:func:`~skald.definitions.get_alignments` for how this
            argument is parsed.
        """
        if isinstance(lines, str):
            self.lines = lines.split("\n")
        else:
            self.lines = lines
        self.width = width
        self.positions = get_positions(positions)
        self.alignments = get_alignments(alignments)
        self.force = force

class Element:
    """Represents a element on the page."""
    def __init__(self, element=None, location=None, size=None,
            allow_overwrite=False):
        """

        :param element: A
            :py:class:`~selenium.webdriver.remote.webelement.WebElement` to
            add tooltips to.
        """
        if element is not None:
            self.location = Point(x=element.location["x"], y=element.location["y"])
            self.size = Size(width=element.size["width"], height=element.size["height"])
        else:
            self.location = location
            self.size = size
        self.allow_overwrite = allow_overwrite
        self.tooltips = []

    def add_tooltip(self, *tooltips):
        """Add a tooltip to this element.

        :param tooltips: A :py:class:`~skald.definitions.Tooltip` to annotate
            this element. Can also be either a string or list of strings that
            will be passed as the ``lines`` argument to
            :py:meth:`~skald.definitions.Tooltip.__init__` and a new
            :py:class:`~skald.definitions.Tooltip` will be created.
        """
        for tooltip in tooltips:
            if isinstance(tooltip, Tooltip):
                self.tooltips.append(tooltip)
            else:
                tooltip_rep = Tooltip(tooltip)
                self.tooltips.append(tooltip_rep)

    @property
    def rectangle(self):
        return Rectangle.from_sizes(size=self.size, point=self.location)

class Document:
    """A document that documents elements in a screenshot."""
    def __init__(self, name, crop=None):
        """

        :param name: The name of the document. This will be used to define
            the path where the resulting document will be saved.
        :param crop: Specify bounds to crop the
            :py:class:`~skald.definitions.Screenshot` this document is based
            on. A 4-tuple of coordinates, such as
            :py:class:`~skald.geometry.Rectangle`.
        """
        self.name = name
        self.elements = []
        self.crop = crop

    def add_element(self, *elements, tooltip=None):
        """Add elements to this document.

        :param elements: Elements to be added to the document, can either be a
            :py:class:`~selenium.webdriver.remote.webelement.WebElement` or a
            :py:class:`~skald.definitions.Element`.
        :param tooltip: Tooltip to be used for ``elements``. Passed directly to
            :py:meth:`~skald.definitions.Element.add_tooltip`, so argument
            should follow the same format.
            
            **Note**: If multiple elements are passed, all of them will be
            assigned the same tooltip.
        """
        for element in elements:
            if isinstance(element, Element):
                if tooltip is not None:
                    element.add_tooltip(tooltip)
                self.elements.append(element)
            else:
                element_rep = Element(element)
                if tooltip is not None:
                    element_rep.add_tooltip(tooltip)
                self.elements.append(element_rep)

class Screenshot:
    """A single screenshot.

    A screenshot can contain multiple documents, which will each use the same
    screenshot as it's base.

    """
    def __init__(self, name, path):
        """Create a new screenshot.

        :param name: The that should be used to represent this screenshot.
        :param path: The path this screenshot should be saved to.
            This should be a directory, as `name` is used to create the actual
            name of the file and metadata file. See
            :py:attr:`~skald.definitions.Screenshot.image_path` and 
            :py:attr:`~skald.definitions.Screenshot.meta_path`.
        """
        self.name = name
        self.documents = []
        self.path = path

    def add_document(self, document):
        """Add a document to the screenshot.
        
        :param document: A :py:class:`~skald.definitions.Document` defining a
            document to be created from this screenshot.
        """
        self.documents.append(document)

    @property
    def image_path(self):
        """The path of the actual imagefile itself."""
        return os.path.join(self.path, "%s.png" % self.name)

    @property
    def meta_path(self):
        """The path of the file containing metadata about the image.

        This is where all the extra information about how to process the image
        to create documents will be saved.
        """
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
                "crop": obj.crop,
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
        elif isinstance(obj, Enum):
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
            obj = Document(document["name"], Rectangle(*document["crop"]))
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
