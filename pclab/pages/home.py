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
from pclab.utils.figure import create_pca_figure
from pclab.utils.common import get_files
from pclab.utils.common import to_binary
from pclab.utils.model import create_model
from pclab.utils.preprocess import to_array
from pclab.utils.preprocess import to_image

register_page(
    __name__,
    path="/",
    title="Home | PCLab",
    description="Principle Component Labeler",
)

layout = [
    html.Div(id="notify_load"),
    Grid(
        p="md",
        children=[
            Col(
                md=3,
                sm=2,
                xs=12,
                p="md",
                children=[
                    TextInput(
                        id="pattern",
                        label="Directory Pattern",
                        description="Accepts absolute or relative path.",
                        size="xs",
                        pb="md",
                        icon=DashIconify(icon="carbon:image-search"),
                        placeholder="i.e. ./instance/*/*.PNG",
                        value="./instance/*/*.PNG",
                    ),
                    NavLink(
                        id="load",
                        icon=DashIconify(icon="ic:outline-upload-file"),
                        label="Load Files",
                    ),
                    NavLink(
                        id="clear",
                        icon=DashIconify(icon="ic:baseline-clear"),
                        label="Clear Database",
                    ),
                    NavLink(
                        id="refresh",
                        icon=DashIconify(icon="ic:baseline-refresh"),
                        label="Refresh Plot",
                    ),
                    NavLink(
                        id="previous",
                        icon=DashIconify(icon="ic:baseline-arrow-back"),
                        label="Previous",
                    ),
                    NavLink(
                        id="next",
                        icon=DashIconify(icon="ic:baseline-arrow-forward"),
                        label="Next",
                    ),
                ]
            ),
            Col(
                md=6,
                sm=8,
                xs=12,
                children=[
                    LoadingOverlay(
                        children=dcc.Graph(id="graph"),
                        loaderProps={"variant": "bars"},
                    )
                ]
            ),
            Col(
                md=3,
                sm=2,
                xs=12,
                children=[
                    Image(
                        id="image",
                        withPlaceholder=True,
                        fit="contain",
                        height=200,
                    ),
                    SegmentedControl(
                        id="label",
                        radius=0,
                        fullWidth=True,
                        disabled=True,
                        data=[],
                    ),
                ]
            ),
        ],
    )
]


@callback(
    Output("label", "data"),
    Input("label", "data"),
)
def update_label_data(value):
    rows = get_db().execute("SELECT title, id FROM label").fetchall()
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
        (Output("pattern", "disabled"), True, False),
        (Output("load", "disabled"), True, False),
        (Output("clear", "disabled"), True, False),
        (Output("refresh", "disabled"), True, False),
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
            db.execute("INSERT INTO sample (blob) VALUES (?)", (blob,))
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
    Output("graph", "selectedData"),
    Input("label", "value"),
    State("graph", "selectedData"),
)
def update_selected_label(label_id, selected_data):
    if selected_data is None:
        return no_update
    id = selected_data["points"][0]["customdata"]
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
    Input("graph", "selectedData"),
)
def update_selected(selected_data):
    if selected_data is None:
        return None, None, True
    id = selected_data["points"][0]["customdata"]
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
    src = to_image(dict(row)["blob"])
    return src, label_id, False


@callback(
    Output("graph", "figure"),
    Input("refresh", "n_clicks"),
)
def update_figure(n_clicks):
    rows = get_db().execute(
        """
        SELECT
            id,
            label_id,
            blob
        FROM sample
        """
    ).fetchall()
    if len(rows) < 1:
        return no_update
    model = create_model()
    ids, labels, blobs = zip(*map(lambda x: dict(x).values(), rows))
    pcs = model.fit_transform(list(map(to_array, blobs)))
    figure = create_pca_figure(ids, labels, pcs)
    return figure


@callback(
    Output("clear", "disabled"),
    Input("clear", "n_clicks"),
)
def update_cleared(n_clicks):
    db = get_db()
    db.execute("DELETE FROM sample")
    db.commit()
    return no_update
