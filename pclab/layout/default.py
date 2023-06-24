#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import clientside_callback
from dash import dcc
from dash import Input
from dash import Output
from dash import page_container
from dash import State
from dash_iconify import DashIconify
from dash_mantine_components import ActionIcon
from dash_mantine_components import Container
from dash_mantine_components import Group
from dash_mantine_components import Header
from dash_mantine_components import MantineProvider
from dash_mantine_components import NotificationsProvider
from dash_mantine_components import Text

header = Header(
    height=28,
    px=5,
    fixed=True,
    children=[
        Group(
            position="apart",
            children=[
                Text(
                    size="xs",
                    children=[
                        DashIconify(
                            icon="raphael:lab",
                            inline=True,
                            color="indigo",
                        ),
                        "PC Lab",
                    ], 
                ),
                Group(
                    spacing=0,
                    children=[
                        ActionIcon(
                            id="source",
                            variant="transparent",
                            children=[
                                DashIconify(
                                    icon="radix-icons:github-logo",
                                ),
                            ]
                        ),
                        ActionIcon(
                            id="color-scheme-toggle",
                            variant="transparent",
                            children=[
                                DashIconify(
                                    icon="radix-icons:blending-mode",
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    ]
)

wrapper = Container(
    id="wrapper",
    fluid=True,
    pt=28,
    children=page_container,
)

clientside_callback(
    """ function(data) { return data } """,
    Output("theme-provider", "theme"),
    Input("theme-store", "data"),
)

clientside_callback(
    """function(n_clicks, data) {
        if (data) {
            if (n_clicks) {
                const scheme = data["colorScheme"] == "dark" ? "light" : "dark"
                return { colorScheme: scheme } 
            }
            return dash_clientside.no_update
        } else {
            return { colorScheme: "light" }
        }
    }""",
    Output("theme-store", "data"),
    Input("color-scheme-toggle", "n_clicks"),
    State("theme-store", "data"),
)

def layout():
    return MantineProvider(
        id="theme-provider",
        theme={"colorScheme": "light"},
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            MantineProvider(
                theme={
                    "primaryColor": "indigo",
                    "fontFamily": "'Roboto', system-ui, sans-serif",
                },
                inherit=True,
                children=[
                    dcc.Store(id="theme-store", storage_type="local"),
                    NotificationsProvider(
                        children=[header, wrapper],
                    ),
                ],
            )
        ],
    )
