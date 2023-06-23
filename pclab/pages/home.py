#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import callback
from dash import dcc
from dash import Input
from dash import Output
from dash import no_update
from dash import State
from dash import register_page
from dash_iconify import DashIconify
from dash_mantine_components import Button
from dash_mantine_components import Col
from dash_mantine_components import Image
from dash_mantine_components import Grid
from dash_mantine_components import Group
from dash_mantine_components import LoadingOverlay
from dash_mantine_components import NavLink
from dash_mantine_components import SegmentedControl
from dash_mantine_components import TextInput

from pclab.db import get_db
from pclab.utils.figure import create_figure
from pclab.utils.common import get_files
from pclab.utils.common import to_binary
from pclab.utils.preprocess import to_image

register_page(
    __name__,
    path="/",
    title="Home | PCLab",
    description="Principle Component Labeler",
)

layout = [
    dcc.Interval(id="interval", max_intervals=0),
    Grid(
        children=[
            Col(
                span=10,
                px=0,
                children=[
                    LoadingOverlay(
                        children=dcc.Graph(id="graph"),
                        loaderProps={"variant": "bars"},
                    )
                ]
            ),
            Col(
                span="auto",
                px=0,
                children=[
                    Image(
                        id="image",
                        withPlaceholder=True,
                        height=160,
                    ),
                    SegmentedControl(
                        id="label",
                        radius=0,
                        fullWidth=True,
                        disabled=True,
                        data=[],
                    ),
                    NavLink(
                        id="previous",
                        icon=DashIconify(icon="carbon:previous-outline"),
                        label="Previous",
                    ),
                    NavLink(
                        id="next",
                        icon=DashIconify(icon="carbon:next-outline"),
                        label="Next",
                    ),
                ]
            ),
            Col(
                span=12,
                px=0,
                children=[
                    Group(
                        children=[
                            TextInput(
                                id="pattern",
                                icon=DashIconify(icon="carbon:image-search"),
                                placeholder="Absolute path or GLOB pattern...",
                                value="./instance/**/*.png",
                            ),
                            Button(
                                id="load",
                                children="Load",
                            ),
                            Button(
                                id="reload",
                                children="Reload",
                            ),
                        ]
                    )
                ],
            ),
        ],
    )
]


@callback(
    Output("label", "data"),
    Input("label", "data"),
)
def update_label(value):
    rows = get_db().execute(
        """
        SELECT title, id FROM label
        """
    ).fetchall()
    data = [{"label": r["title"], "value": str(r["id"])} for r in rows]
    return data


@callback(
    Output("pattern", "value"),
    Input("load", "n_clicks"),
    State("pattern", "value"),
    prevent_initial_call=True,
)
def load_files(n_clicks, pattern):
    paths = get_files(pattern)
    db = get_db()
    db.execute("PRAGMA foreign_keys = ON")
    for path in paths:
        blob = to_binary(path)
        db.execute(
            """
            INSERT INTO sample (
                path, blob, label_id
            ) VALUES (?, ?, 1)
            """,
            (path, blob),
        )
    db.commit()
    return no_update


@callback(
    Output("graph", "figure"),
    Input("reload", "n_clicks"),
)
def update_figure(pattern):
    rows = get_db().execute(
        """
        SELECT
            id,
            label_id,
            blob
        FROM sample
        """,
    ).fetchall()
    figure = create_figure(rows)
    return figure

@callback(
    Output("label", "value"),
    Output("label", "disabled"),
    Output("image", "src"),
    Input("graph", "clickData"),
    prevent_initial_call=True,
)
def update_clicked(data):
    if not isinstance(data, dict):
        None, True, None
    id = data["points"][0]["customdata"]
    row = get_db().execute(
        """
        SELECT
            label_id,
            blob
        FROM sample WHERE id = ? 
        """,
        (id,)
    ).fetchone()
    label_id = str(dict(row)["label_id"])
    blob = dict(row)["blob"]
    src = to_image(blob) 
    return label_id, False, src
