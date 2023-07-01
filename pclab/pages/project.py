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
from pclab.utils.pipeline import create_pipeline
from pclab.utils.preprocess import to_array
from pclab.utils.preprocess import to_image

register_page(__name__, path_template="/project/<slug>")

def layout(slug = None):
    return [
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
                            p=0,
                            children=[
                                AgGrid(
                                    id="grid",
                                    defaultColDef={"sortable": True},
                                    rowModelType="infinite", 
                                    dashGridOptions={
                                        "rowBuffer": 0,
                                        "maxBlocksInCache": 1,
                                        "rowSelection": "multiple",
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        )
    ]


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
    arrays = list(map(lambda r: to_array(r["blob"]), records))
    pipeline = create_pipeline()
    pcs = pipeline.fit_transform(arrays).tolist()
    data = map(
        lambda x: {
            "id": x[0]["id"],
            "label": x[0]["label_id"],
            "pc": x[1],
            "title": x[0]["label_title"],
            "color": x[0]["color"],
        }, 
        zip(records, pcs)
    )
    return list(data)


@callback(
    Output("graph", "figure"),
    Input("store", "data"),
)
def update_figure(data):
    if data is None:
        return no_update
    ids, labels, pcs, titles, colors = zip(*map(lambda x: x.values(), data))
    figure = create_figure(ids, labels, pcs, titles, colors)
    return figure


@callback(
    Output("grid", "getRowsResponse"),
    Input("grid", "getRowsRequest"),
    State("store", "data"),
)
def update_row_request(request, data):
    if request is None:
        return no_update
    partial = data[request["startRow"] : request["endRow"]]
    return {"rowData": partial, "rowCount": len(data)}
