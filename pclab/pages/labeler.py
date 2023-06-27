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
from dash_mantine_components import SegmentedControl

from pclab.db import get_db
from pclab.utils.figure import create_figure
from pclab.utils.model import create_model
from pclab.utils.preprocess import to_array
from pclab.utils.preprocess import to_image

register_page(
    __name__,
    path_template="/project/<project_id>",
    title="Labeler | PCLab",
    description="Principle Component Labeler",
)

def layout(project_id=None):
    return [
        dcc.Store(id="project_id", data=project_id),
        dcc.Interval(id="interval", max_intervals=0),
        Grid(
            px="sm",
            py="lg",
            children=[
                Col(
                    sm=9,
                    xs=12,
                    children=[
                        LoadingOverlay(
                            loaderProps={"variant": "bars"},
                            children=dcc.Graph(id="graph"),
                        )
                    ]
                ),
                Col(
                    sm=3,
                    xs=12,
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
    Output("interval", "n_intervals"),
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
    Output("image", "alt"),
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
    label_id = str(dict(row)["label_id"])
    alt = dict(row)["filename"]
    src = to_image(dict(row)["blob"])
    return alt, src, label_id, False


@callback(
    output=Output("graph", "figure"),
    inputs=Input("project_id", "data"),
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
    Output("select", "data"),
    Input("select", "data"),
)
def update_select(data):
    rows = get_db().execute("SELECT title, id FROM project")
    if rows is None:
        return no_update
    records = map(dict, rows)
    data = [dict(label=r["title"], value=r["id"]) for r in records]
    return data