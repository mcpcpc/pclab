#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import callback
from dash import Input
from dash import no_update
from dash import Output
from dash import register_page
from dash_mantine_components import Anchor
from dash_mantine_components import Button
from dash_mantine_components import Group
from dash_mantine_components import Stack
from dash_mantine_components import Text
from dash_mantine_components import Title

from pclab.db import get_db

register_page(__name__, path_template="/")

layout = [
    Stack(
        spacing="lg",
        p="xl",
        align="center",
        justify="center",
        children=[
            Group(
                align="center",
                children=[
                    Title("Data Labeling Assisted by"),
                    Title("Machine Learning", variant="gradient")
                ]
            ),
            Text("Select a project from the list below to begin labeling.", size="xl"),
            Group(
                id="group",
                position="center",
                spacing="xl",
            ),
        ],
    ),
]

@callback(
    Output("group", "children"),
    Input("group", "children"),
)
def update_projects_list(children):
    rows = get_db().execute("SELECT * FROM project").fetchall()
    if len(rows) < 1:
        return no_update
    records = list(map(dict, rows))
    return [
        Anchor(
            href=f"/project/{r['slug']}",
            children=[
                Button(
                    children=r["title"],
                    radius="xl",
                    size="lg",
                )
            ],
        ) for r in records
    ]
