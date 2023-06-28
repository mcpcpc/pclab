#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plotly.graph_objects import Figure
from plotly.graph_objects import Scattergl


def create_figure(ids: list, labels: list, pcs: list, titles: list, colors: list):
    figure = Figure()
    figure.update_layout(margin=dict(t=0, r=0, b=0, l=0))
    figure.update_layout(modebar_orientation="v", showlegend=False)
    figure.update_layout(clickmode="event+select")
    figure.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    figure.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    figure.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    figure.update_yaxes(showticklabels=False, showgrid=False, zeroline=False) 
    if len(ids) < 1:
        return figure
    for title, label, color in set(zip(titles, labels, colors)):
        figure.add_trace(
            Scattergl(
                x=[pc[0] for pc, l in zip(pcs, labels) if label == l],
                y=[pc[1] for pc, l in zip(pcs, labels) if label == l],
                customdata=[id for id, l in zip(ids, labels) if label == l],
                name=title,
                mode="markers",
                marker={
                    "line_width": 1,
                    "color": color,
                }
            ),
        )
    return figure