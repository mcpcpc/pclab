#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plotly.graph_objects import Figure
from plotly.graph_objects import Scatter
from sklearn.decomposition import PCA


def create_components(data):
    pca = PCA(n_components=2, random_state=0)
    return pca.fit_transform(data)


def create_figure(data):
    figure = Figure()
    figure.add_trace(
        Scatter(

        ),
    )
    figure.update_layout(margin=dict(t=0, r=0, b=0, l=0))
    figure.update_layout(modebar_orientation="v")
    figure.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    figure.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    return figure