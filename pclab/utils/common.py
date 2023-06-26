#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob
from functools import reduce
from pathlib import Path
from typing import Callable

Preprocessor = Callable[[list[dict]], list[dict]]


def compose(*functions: Preprocessor) -> Preprocessor:
    return reduce(lambda f, g: lambda x: g(f(x)), functions)
