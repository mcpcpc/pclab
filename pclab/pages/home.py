#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dash import callback
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
    html.Div(id="notify_load"),
    dcc.Store(id="selection_cache"),
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
                px=0,
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
    output=Output("notify_load", "children"),
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
    Output("selection_cache", "data"),
    Input("graph", "selectedData"),
)
def update_selection_cache(selected_data):
    if not isinstance(selected_data, dict):
        return None
    return selected_data["points"][0]["customdata"]
    

@callback(
    Output("graph", "selectedData"),
    Input("label", "value"),
    State("selection_cache", "data"),
)
def update_selected_label(label_id, id):
    if id is None:
        return no_update
    if id == {}:
        return no_update
    db = get_db()
    db.execute("PRAGMA foreign_keys = ON")
    db.execute(
        """
        UPDATE sample SET
            updated_at = CURRENT_TIMESTAMP,
            label_id = ?
        WHERE id = ?
        """,
        (label_id, id),
    )
    db.commit()
    return no_update


@callback(
    Output("image", "src"),
    Output("label", "value"),
    Output("label", "disabled"),
    Input("selection_cache", "data"),
)
def update_selected(id):
    if id is None:
        return None, None, True
    row = get_db().execute(
        "SELECT label_id, blob FROM sample WHERE id = ?",
        (id,)
    ).fetchone()
    label_id = str(dict(row)["label_id"])
    src = to_image(dict(row)["blob"])
    return src, label_id, False


@callback(
    Output("graph", "figure"),
    Input("reload", "n_clicks"),
)
def update_figure(n_clicks):
    rows = get_db().execute("SELECT id, label_id, blob FROM sample").fetchall()
    figure = create_figure(rows)
    return figure
