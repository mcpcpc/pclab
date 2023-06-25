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
from dash_mantine_components import Col
from dash_mantine_components import Image
from dash_mantine_components import Grid
from dash_mantine_components import Group
from dash_mantine_components import LoadingOverlay
from dash_mantine_components import NavLink
from dash_mantine_components import SegmentedControl

from pclab.db import get_db
from pclab.utils.figure import create_figure
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
    Grid(
        p="md",
        children=[
            Col(
                md=3,
                xs=12,
                p="md",
                children=[
                    NavLink(
                        id="refresh",
                        icon=DashIconify(icon="ic:baseline-refresh"),
                        label="Refresh",
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
                sm=9,
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
                sm=3,
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
    output=Output("graph", "figure"),
    inputs=Input("refresh", "n_clicks"),
    background=True,
    running=[
        (Output("refresh", "disabled"), True, False),
    ],
)
def update_figure(n_clicks):
    rows = get_db().execute(
        """
        SELECT
            sample.id AS id,
            sample.label_id AS label_id,
            sample.blob AS blob,
            label.title AS label_title,
            label.color AS color
        FROM sample
            INNER JOIN label ON label.id = sample.label_id
        """
    ).fetchall()
    if len(rows) < 1:
        return no_update
    model = create_model()
    ids, labels, blobs, titles, colors = zip(*map(lambda x: dict(x).values(), rows))
    pcs = model.fit_transform(list(map(to_array, blobs)))
    figure = create_figure(ids, labels, pcs, titles, colors)
    return figure
