# -*- coding: utf-8 -*-
import os
import json
from itertools import product

from PIL import Image, ImageFont, ImageDraw

from .geometry import Size, Point, Rectangle
from .text import TextArea, TextAlign
from .positioning import get_box_position, Choice
from .definitions import load

def get_output_file(image_path, document_name, config):
    relative_image_dir = os.path.dirname(image_path)
    output = os.path.join(config.output, relative_image_dir, "%s.png" % document_name)
    return output

def draw_textarea(draw, textarea, config):
    """Draws a tooltip on the image."""
    font = config.font.get_font()

    print("Drawing textarea at", textarea.rectangle)
    draw.rectangle(textarea.rectangle, fill=config.tooltip.color)
    for i, line in enumerate(textarea.text):
        position = textarea.get_line_position(i)
        draw.text(position, line, font=font, fill=config.font.color)

def get_textarea(tooltip, element, bounds, config, avoid):
    font = config.font.get_font()

    textarea = TextArea.from_lines(
        lines=tooltip.lines,
        font=font,
        line_spacing=config.tooltip.line_spacing,
        padding=config.tooltip.padding,
        align=TextAlign.center)

    textarea.choices = get_box_position(element, tooltip, textarea.size,
            bounds, config.tooltip.margin, avoid=avoid,
            penalties=config.penalties)

    return textarea


def make_combinations(textareas):
    choice_lists = []
    for textarea in textareas:
        choices = []
        for choice in textarea.choices:
            choices.append({"textarea": textarea, "choice": choice})
        choice_lists.append(choices)
    return list(product(*choice_lists))

def best_combinations(combinations):
    """Selects the best combination of positions for `textareas` based on each
    textarea's positional choices and their relative punshiment, disallowing
    any overlap between textareas.
    """
    indices = set()
    for i, combination in enumerate(combinations):
        crash = False
        for c1 in combination:
            for c2 in combination:
                if c1["textarea"] != c2["textarea"]:
                    if c1["choice"].rectangle in c2["choice"].rectangle:
                        crash = True
        if not crash:
            indices.add(i)
    combinations = [c for i, c in enumerate(combinations) if i in indices]
    combinations.sort(key=lambda x: sum([y["choice"].penalty for y in x]))
    combination = combinations[0]
    for area in combination:
        area["textarea"].position = area["choice"].rectangle.position

def process_document(base_image, document, config, output):
    """Process a single document and create a documented screenshot."""
    img = Image.open(base_image).copy()
    if document.crop is not None:
        img = img.crop(document.crop)

    draw = ImageDraw.Draw(img)

    image_size = Size(*img.size)

    textareas = []

    for element in document.elements:
        for tooltip in element.tooltips:
            textarea = get_textarea(tooltip=tooltip,
                    element=element,
                    bounds=image_size,
                    config=config,
                    avoid=document.elements)
            textareas.append(textarea)

    combinations = make_combinations(textareas)
    best_combinations(combinations)

    for textarea in textareas:
        draw_textarea(draw, textarea, config)

    print("Saving to file", output)
    img.save(output)

def process_screenshots(screenshots, config):
    """Processes each screenshot to generate a documented screenshot."""
    for screenshot in screenshots:
        metadata = load(screenshot["metadata"])
        for document in metadata.documents:
            output = get_output_file(metadata.image_path, document.name, config)
            process_document(
                base_image=os.path.join(config.input, metadata.image_path),
                document=document, config=config, output=output)

def get_screenshots(path):
    """Retrieves all screenshots with JSON metadata from the specified path."""
    json_files = {}
    image_files = {}

    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            file_name, file_extension = os.path.splitext(file_path)
            if file_extension == ".json":
                json_files[file_name] = os.path.abspath(file_path)
            elif file_extension == ".png":
                image_files[file_name] = os.path.abspath(file_path)
    matching_files = []
    for image_file in image_files:
        if image_file in json_files:
            matching_files.append({
                "image": image_files[image_file],
                "metadata": json_files[image_file]
                })
    return matching_files
