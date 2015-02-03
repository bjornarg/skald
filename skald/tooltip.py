# -*- coding: utf-8 -*-
from .geometry import Size

def get_wrapping_box_size(size, padding):
    return Size(size.width+padding*2, size.height+padding*2)
