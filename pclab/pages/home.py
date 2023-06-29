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
from dash_mantine_components import Card
from dash_mantine_components import CardSection
from dash_mantine_components import Chip
from dash_mantine_components import ChipGroup
from dash_mantine_components import Col
from dash_mantine_components import Image
from dash_mantine_components import Grid
from dash_mantine_components import Group
from dash_mantine_components import LoadingOverlay
from dash_mantine_components import SegmentedControl
from dash_mantine_components import Stack
from dash_mantine_components import TextInput

from pclab.db import get_db
from pclab.utils.figure import create_figure
from pclab.utils.model import create_model
from pclab.utils.preprocess import to_array
from pclab.utils.preprocess import to_image

register_page(__name__, path="/")

layout = [
    dcc.Interval(id="interval", max_intervals=0),
    Grid(
        pt="sm",
        gutter="sm",
        align="stretch",
        children=[
            Col(
                xs=12,
                children=[
                    ChipGroup(id="chip_group"),
                ],
            ),
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
                            CardSection(
                                children=[
                                    LoadingOverlay(
                                        loaderProps={"variant": "bars"},
                                        children=Image(
                                            id="image",
                                            withPlaceholder=True,
                                            fit="cover",
                                            height=200,
                                        ), 
                                    ),
                                ]
                            ),
                            Stack(
                                children=[
                                    TextInput(
                                        id="filename",
                                        icon=DashIconify(
                                            icon="ic:baseline-image"
                                        ),
                                        mt="md",
                                        disabled=True,
                                    ),
                                    SegmentedControl(
                                        id="label",
                                        radius=0,
                                        fullWidth=True,
                                        disabled=True,
                                        data=[],
                                    ),
                                ],
                            ),
                        ]
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
    rows = get_db().execute(
        """
        SELECT
            title,
            id
        FROM label
        """
    ).fetchall()
    #data = [{"label": r["title"], "value": str(r["id"])} for r in rows]
    #return data
    data = map(lambda r: dict(label=r["title"], value=str(r["id"])), rows)
    return list(data)
    

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
    Output("filename", "value"),
    Output("image", "src"),
    Output("label", "value"),
    Output("label", "disabled"),
    Input("graph", "selectedData"),
)
def update_selected(selected_data):
    if selected_data is None:
        return None, None, None, True
    id = selected_data["points"][0]["customdata"]
    row = get_db().execute(
        """
        SELECT
            label_id,
            filename,
            blob
        FROM sample WHERE id = ?
        """,
        (id,)
    ).fetchone()
    alt = dict(row)["filename"]
    src = to_image(dict(row)["blob"])
    label_id = str(dict(row)["label_id"])
    return alt, src, label_id, False


@callback(
    output=Output("graph", "figure"),
    inputs=Input("chip_group", "value"),
    background=True,
)
def update_figure(project_id):
    if project_id is None:
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
            INNER JOIN label ON label.id = sample.label_id
        WHERE project_id = ?
        """,
        (project_id,),
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
    model = create_model()
    ids, labels, blobs, titles, colors = zip(*map(lambda x: x.values(), records))
    pcs = model.fit_transform(list(map(to_array, blobs)))
    figure = create_figure(ids, labels, pcs, titles, colors)
    return figure


@callback(
    Output("chip_group", "children"),
    Input("chip_group", "children"),
)
def update_select(data):
    rows = get_db().execute("SELECT title, id FROM project")
    if rows is None:
        return no_update
    records = map(dict, rows)
    children = map(lambda r: Chip(r["title"], value=str(r["id"])), records)
    return list(children)