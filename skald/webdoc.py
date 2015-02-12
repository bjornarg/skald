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
    output = os.path.join(config.folder, relative_image_dir, "%s.png" % document_name)
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

def get_image_size_from_crop(crop, image_size):
    new_size = list(crop)
    if crop.left == "*" or crop.left == ".":
        new_size[0] = 0
    if crop.top == "*" or crop.top == ".":
        new_size[1] = 0
    if crop.right == "*" or crop.right == ".":
        new_size[2] = image_size.width
    if crop.bottom == "*" or crop.bottom == ".":
        new_size[3] = image_size.height
    return Rectangle(*new_size)

def get_actual_crop_area(crop, image_size, all_elements, margin):
    crop = list(crop)
    if crop[0] == "*":
        crop[0] = min([r.left for r in all_elements]) - margin
    elif crop[0] == ".":
        crop[0] = 0

    if crop[1] == "*":
        crop[1] = min([r.top for r in all_elements]) - margin
    elif crop[1] == ".":
        crop[1] = 0

    if crop[2] == "*":
        crop[2] = max([r.right for r in all_elements]) + margin
    elif crop[2] == ".":
        crop[2] = image_size.width

    if crop[3] == "*":
        crop[3] = max([r.bottom for r in all_elements]) + margin
    elif crop[3] == ".":
        crop[3] = image_size.height

    return Rectangle(*crop)

def process_document(base_image, document, config, output):
    """Process a single document and create a documented screenshot."""
    img = Image.open(base_image).copy()
    image_size = document.crop
    if image_size is not None:
        image_size = get_image_size_from_crop(image_size, Size(*img.size))
    else:
        image_size = Rectangle.from_sizes(position=Point(0,0),
                size=Size(*img.size))

    draw = ImageDraw.Draw(img)

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

    text_area_rectangles = []

    for textarea in textareas:
        draw_textarea(draw, textarea, config)
        text_area_rectangles.append(textarea.rectangle)

    all_elements = text_area_rectangles + [e.rectangle for e in document.elements]
    crop = get_actual_crop_area(document.crop, Size(*img.size), all_elements, config.tooltip.margin)

    img = img.crop(box=crop)

    print("Saving to file", output)
    img.save(output)

def process_screenshots(screenshots, config):
    """Processes each screenshot to generate a documented screenshot."""
    for screenshot in screenshots:
        metadata = load(screenshot["metadata"])
        for document in metadata.documents:
            output = get_output_file(metadata.image_path, document.name, config)
            process_document(
                base_image=os.path.join(config.folder, metadata.image_path),
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
