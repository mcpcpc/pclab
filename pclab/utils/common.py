#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode
from glob import glob
from io import BytesIO

def get_files(pattern):
    return glob(pattern)

def to_binary(filename: str):
    with open(filename, 'rb') as file:
        blob = file.read()
    return blob

def to_dataurl(blob):
    pass

def from_binary(blob):
    pass

def get_image_data():
    pass
