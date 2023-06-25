#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import BytesIO

from PIL import Image

from pclab.utils.common import compose

def to_image(blob) -> Image:
    binary_stream = BytesIO(blob)
    return Image.open(binary_stream)


def greyscale(image: Image) -> Image:
    return image.convert("L")


def resize(image: Image) -> Image:
    return image.resize((20, 20))


def get_greyscale_values(image: Image) -> list:
    return list(image.getdata())


def to_array(blob: str) -> list:
    preprocessor = compose(
        to_image,
        greyscale,
        resize,
        get_greyscale_values
    )
    return preprocessor(blob)