#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import html
from dash import page_container

header = html.Header(
    id="header",
    style={
        "position": "fixed",
        "display": "block",
        "height": "50px",
        "padding": "0 auto",
        "border-bottom": "1px solid rgb(186, 191, 199)",
        
    },
    children=[
        "PC LAb"
    ], 
)

wrapper = html.Div(
    id="wrapper",
    style={
        "padding-top": "50px",
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