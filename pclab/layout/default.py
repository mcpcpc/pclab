#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import html
from dash import page_container

header = html.Header(
    id="header",
    style={
        "position": "fixed",
        "height": "3em",
    },
    children=[
    ], 
)

wrapper = html.Div(
    id="wrapper",
    style={"padding-top": "3em"},
    children=page_container,
)


def layout(values, version):
    return html.Div(
        children=[
            header,
            wrapper,
        ]
    ) 