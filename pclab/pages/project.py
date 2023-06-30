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
from dash_ag_grid import AgGrid
from dash_mantine_components import Card
from dash_mantine_components import Col
from dash_mantine_components import Grid
from dash_mantine_components import LoadingOverlay

from pclab.db import get_db
from pclab.utils.figure import create_figure
from pclab.utils.pipeline import create_model
from pclab.utils.preprocess import to_array
from pclab.utils.preprocess import to_image

register_page(__name__, path_template="/project/<slug>")

def layout(slug = None):
    return [
        dcc.Interval(id="interval", max_intervals=0),
        dcc.Store(id="slug", data=slug),
        dcc.Store(id="store"),
        Grid(
            pt="sm",
            gutter="sm",
            align="stretch",
            children=[
                Col(
                    sm=9,
                    xs=12,
                    children=[
                        Card(
                            p=0,
                            children=[
                                LoadingOverlay(
                                    loaderProps={"variant": "bars"},
                                    children=dcc.Graph(id="graph"),
                                ),
                            ]
                        ),
                    ],
                ),
                Col(
                    sm=3,
                    xs=12,
                    children=[
                        Card(
                            withBorder=True,
                            children=[
                                AgGrid(
                                    id="grid",
                                    rowModelType="infinite",
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        )
    ]


@callback(
    Output("interval", "n_intervals"),
    Input("label", "value"),
    State("graph", "selectedData"),
)
def update_selected_label(label_id, selected_data):
    if selected_data is None:
        return no_update
    db = get_db()
    for point in selected_data["points"]:
        id = point["customdata"]
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
    output=Output("store", "data"),
    inputs=Input("slug", "data"),
    background=True,
)
def update_figure(slug):
    if slug is None:
        return no_update
    cursor = get_db().execute(
        """
        SELECT
            sample.id AS id,
            sample.label_id AS label_id,
            sample.blob AS blob,
            label.title AS label_title,
            label.color AS color
        FROM sample
        INNER JOIN label
            ON label.id = sample.label_id
        INNER JOIN project
            ON project.id = sample.project_id
        WHERE project.slug = ?
        ORDER BY RANDOM()
        """,
        (slug,),
    )
    records = []
    while True:
        rows = cursor.fetchmany(1000)
        if not isinstance(rows, list):
            break
        if len(rows) < 1:
            break 
        records += list(map(dict, rows))
    if len(records) < 1:
        return no_update
    ids, labels, blobs, titles, colors = zip(*map(lambda x: x.values(), records))
    model = create_model()
    pcs = model.fit_transform(list(map(to_array, blobs)))
    return list(zip((ids, labels, pcs, titles, colors)))


@callback(
    Output("graph", "figure"),
    Input("store", "data"),
)
def update_figure(data):
    if data is None:
        return no_update
    ids, labels, pcs, titles, colors = zip(*data)
    figure = create_figure(ids, labels, pcs, titles, colors)
    return figure
    