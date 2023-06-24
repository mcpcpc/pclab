#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import callback
from dash import ctx
from dash import dcc
from dash import html
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
from dash_mantine_components import Notification
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
    html.Div(id="notify"),
    Grid(
        children=[
            Col(
                sm=10,
                xs=12,
                px=0,
                children=[
                    LoadingOverlay(
                        children=dcc.Graph(id="graph"),
                        loaderProps={"variant": "bars"},
                    )
                ]
            ),
            Col(
                sm=2,
                xs=12,
                children=[
                    Image(
                        id="image",
                        withPlaceholder=True,
                        fit="contain",
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
                                value="./instance/*/*.PNG",
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
def update_label_data(value):
    rows = get_db().execute(
        """
        SELECT title, id FROM label
        """
    ).fetchall()
    data = [{"label": r["title"], "value": str(r["id"])} for r in rows]
    return data


@callback(
    output=Output("notify", "children"),
    inputs=[
        Input("load", "n_clicks"),
        State("pattern", "value"),
    ],
    background=True,
    running=[
        (Output("load", "loading"), True, False),
        (Output("pattern", "disabled"), True, False),
    ],
    prevent_initial_call=True,
)
def load_files(n_clicks, pattern):
    paths = get_files(pattern)
    db = get_db()
    for path in paths:
        blob = to_binary(path)
        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.execute(
                """
                INSERT INTO sample (blob) VALUES (?)
                """,
                (blob,),
            )
            db.commit()
        except db.Error as error:
            return Notification(
                id="warning",
                icon=DashIconify(icon="ic:baseline-warning"),
                title="Warning",
                message=f"{error}",
                color="yellow",
                action="show",
            )
    return Notification(
        id="complete",
        icon=DashIconify(icon="ic:round-celebration"),
        title="Complete",
        message="All images processed.",
        color="blue",
        action="show",
    )


@callback(
    Output("graph", "figure"),
    Output("image", "src"),
    Output("label", "value"),
    Output("label", "disabled"),
    Input("reload", "n_clicks"),
    Input("label", "value"),
    Input("graph", "selectedData"),
)
def update_figure(n_clicks, label_id, selected_data):
    db = get_db()
    src = no_update
    figure = no_update
    disabled = no_update
    label_id_current = no_update
    triggered_id = ctx.triggered_id
    print(triggered_id)
    if triggered_id == "graph" and isinstance(selected_data, dict):
        id = selected_data["points"][0]["customdata"]
        row = get_db().execute("SELECT label_id, blob FROM sample WHERE id = ?", (id,)).fetchone()
        label_id_current = str(dict(row)["label_id"])
        blob = dict(row)["blob"]
        src = to_image(blob)
        disabled = False
    elif triggered_id == "graph" and selected_data is None:
        src = None
        disabled = True
    elif triggered_id == "label" and isinstance(selected_data, dict):
        id = selected_data["points"][0]["customdata"]
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("UPDATE sample set label_id = ? WHERE id = ?", (label_id, id))
        db.commit()
        rows = db.execute("SELECT id, label_id, blob FROM sample").fetchall()
        figure = create_figure(rows)
    elif triggered_id == "reload":
        rows = db.execute("SELECT id, label_id, blob FROM sample").fetchall()
        figure = create_figure(rows)        
    return figure, src, label_id_current, disabled
