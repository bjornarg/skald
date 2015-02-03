# -*- coding: utf-8 -*-
import os
import json

from PIL import Image, ImageFont, ImageDraw

from .geometry import Size, Point, Box, Rectangle
from .text import TextArea, TextAlign
from .positioning import get_box_position
from .definitions import load

def get_output_file(image_path, config):
    relative_image_path = os.path.relpath(image_path, config.input)
    relative_image_dir = os.path.dirname(relative_image_path)
    image_name = os.path.basename(image_path)
    output = os.path.join(config.output, relative_image_dir, image_name)
    return output

def draw_tooltip(draw, tooltip, element, config):
    """Draws a tooltip on the image."""
    font = config.font.get_font()

    textarea = TextArea.from_lines(
        lines=tooltip.lines,
        font=font,
        line_spacing=config.tooltip.line_spacing,
        padding=config.tooltip.padding,
        align=TextAlign.right)

    textarea.position = get_box_position(element, tooltip, textarea.size, config.tooltip.margin)

    draw.rectangle(textarea.rectangle, fill=config.tooltip.color)
    for i, line in enumerate(tooltip.lines):
        position = textarea.get_line_position(i)
        draw.text(position, line, font=font, fill=config.font.color)

def process_document(base_image, document, config, output):
    """Process a single document and create a documented screenshot."""
    img = Image.open(base_image).copy()

    draw = ImageDraw.Draw(img)

    for element in document.elements:
        for tooltip in element.tooltips:
            draw_tooltip(draw, tooltip, element, config)

    img.save(output)

def process_screenshots(screenshots, config):
    """Processes each screenshot to generate a documented screenshot."""
    for screenshot in screenshots:
        metadata = load(screenshot["metadata"])
        for document in metadata.documents:
            output = get_output_file(metadata.image_path, config)
            process_document(metadata.image_path, document, config, output)

def get_screenshots(path):
    """Retrieves all screenshots with JSON metadata from the specified path."""
    json_files = {}
    image_files = {}

    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            file_name, file_extension = os.path.splitext(file_path)
            if file_extension == ".json":
                json_files[file_name] = file_path
            elif file_extension == ".png":
                image_files[file_name] = file_path
    matching_files = []
    for image_file in image_files:
        if image_file in json_files:
            matching_files.append({
                "image": image_files[image_file],
                "metadata": json_files[image_file]
                })
    return matching_files
