# -*- coding: utf-8 -*-
from .configuration import read_configuration
from .webdoc import process_screenshots, get_screenshots

def main():
    config = read_configuration()
    process_screenshots(get_screenshots(config.input), config)
