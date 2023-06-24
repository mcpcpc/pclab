#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plotly.graph_objects import Figure
from plotly.graph_objects import Scattergl
from sklearn.decomposition import PCA

from pclab.utils.preprocess import to_array


def create_components(array: list) -> list:
    pca = PCA(n_components=2, random_state=0)
    return pca.fit_transform(array)


def to_inputs(data: list) -> tuple:
    records = list(map(dict, data))
    unpacked = zip(*map(lambda x: x.values(), records))
    return tuple(unpacked)


def create_figure(data: list):
    figure = Figure()
    figure.update_layout(margin=dict(t=0, r=0, b=0, l=0))
    figure.update_layout(modebar_orientation="v", showlegend=False)
    figure.update_layout(clickmode="event+select")
    figure.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    figure.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    if len(data) < 1:
        return figure
    ids, labels, blobs = to_inputs(data)
    values = list(map(to_array, blobs))
    pcs = create_components(values)
    for label in set(labels):
        figure.add_trace(
            Scattergl(
                x=[pc[0] for pc, l in zip(pcs, labels) if label == l],
                y=[pc[1] for pc, l in zip(pcs, labels) if label == l],
                customdata=[id for id, l in zip(ids, labels) if label == l],
                mode="markers",
            ),
        )
    return figure