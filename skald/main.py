# -*- coding: utf-8 -*-
from .configuration import read_configuration
from .webdoc import process_screenshots, get_screenshots

def main(config_path=None):
    config = read_configuration(config_path)
    process_screenshots(get_screenshots(config.folder), config)
