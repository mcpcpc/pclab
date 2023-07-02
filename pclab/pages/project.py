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

from pclab.db import get_db
from pclab.utils.figure import create_figure
from pclab.utils.pipeline import create_pipeline
from pclab.utils.preprocess import to_array
from pclab.utils.preprocess import to_image

register_page(__name__, path_template="/project/<slug>")

def layout(slug = None):
    return [
        dcc.Store(id="slug", data=slug),
        html.Div(
            style={
                "display": "flex",
                "flex-wrap": "wrap",
                "align-items": "stretch",
            },
            children=[
                html.Div(
                    style={
                        "flex": 1,
                        "border": "1px solid rgb(186, 191, 199)",
                    },
                    children=[
                        dcc.Loading(
                            children=[
                                dcc.Graph(id="graph"),
                            ]
                        ),
                    ]
                ),
                AgGrid(
                    id="grid",
                    style={
                        "flex": 1,
                    },
                    columnDefs=[  
                        {
                            "headerName": "Sample",
                            "field": "image",
                            "cellRenderer": "ImgThumbnail",
                             "width": 100,
                        },
                        {
                            "field": "label",
                        },
                        {
                            "field": "filename",
                        },
                    ],
                    rowModelType="infinite",
                    dashGridOptions={
                        "rowBuffer": 0,
                        "maxBlocksInCache": 1,
                        "rowSelection": "multiple",
                        "rowHeight": 100,
                        "noRowsOverlayComponent": "CustomNoRowsOverlay",
                        "noRowsOverlayComponentParams": {
                            "message": "No data selected",
                            "fontSize": 12,
                        },
                    },
                ),
            ],
        )
    ]


@callback(
    output=Output("graph", "figure"),
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
    ids, labels, _, titles, colors = zip(*map(lambda x: x.values(), records))
    pipeline = create_pipeline()
    pcs = pipeline.fit_transform(arrays).tolist()
    figure = create_figure(ids, labels, pcs, titles, colors)
    return figure


@callback(
    Output("grid", "getRowsResponse"),
    Input("grid", "getRowsRequest"),
    Input("graph", "selectedData"),
)
def update_row_request(request, selected_data):
    if request is None:
        return no_update
    if selected_data is None:
        #return no_update
        return {"rowData": [], "rowCount": 0}
    if not isinstance(selected_data["points"], list):
        return {"rowData": [], "rowCount": 0}
    if len(selected_data["points"]) < 1:
        #return no_update
        return {"rowData": [], "rowCount": 0}
    data = [] 
    for point in selected_data["points"]:
        id = point["customdata"]
        row = get_db().execute(
            """
            SELECT
                sample.id AS id,
                sample.blob AS image,
                sample.filename AS filename,
                sample.label_id AS label_id,
                label.title AS label
            FROM sample
            INNER JOIN label
                ON label.id = sample.label_id
            WHERE sample.id = ? 
            """,
            (id,),
        ).fetchone()
        data.append(dict(row))
    for i, d in enumerate(data):
        data[i]["image"] = to_image(d["image"])
    partial = data[request["startRow"] : request["endRow"]]
    return {"rowData": partial, "rowCount": len(data)}
