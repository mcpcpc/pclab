#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import html
from dash import page_container

header = html.Header(
    id="header",
    style={
        "width": "100%",
        "display": "block",
        "height": "50px",
        "padding": "auto 1em",
        "border-bottom": "1px solid rgb(186, 191, 199)",
        
    },
    children=[
        "PC Lab"
    ], 
)

wrapper = html.Div(
    id="wrapper",
    style={
    },
    children=page_container,
)


def layout(values, version):
    return html.Div(
        children=[
            header,
            wrapper,
        ]
    ) 