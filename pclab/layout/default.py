#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import html
from dash import page_container

wrapper = html.Div(
    id="wrapper",
    children=page_container,
)


def layout(values, version):
    return [
        wrapper,
    ]