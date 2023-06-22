#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode
from glob import glob
from io import BytesIO

from PIL import Image


def get_files(pattern) -> list:
    return glob(pattern)


def to_binary(filename: str):
    with open(filename, 'rb') as file:
        blob = file.read()
    return blob


def to_image(blob) -> Image:
    binary_stream = BytesIO(blob)
    image = Image.open(binary_stream)
    return image
