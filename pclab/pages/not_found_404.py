#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import register_page
from dash_iconify import DashIconify
from dash_mantine_components import Anchor
from dash_mantine_components import Stack
from dash_mantine_components import Text

register_page(
    __name__,
    path="/404"
)

layout = [
    Stack(
        align="center",
        p="xl",
        children=[
            DashIconify(icon="ri:emotion-sad-line", width=50),
            Text(
                [
                    "If you think this page should exist, create an issue ",
                    Anchor("here", underline=False, href="#"),
                    ".",
                ]
            ),
            Anchor("Go back to home ->", href="/project/1", underline=False),
        ],
    )
]
