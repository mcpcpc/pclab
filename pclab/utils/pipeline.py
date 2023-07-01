#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline


def create_pipeline() -> Pipeline:
    pipeline = Pipeline(
        steps=[
            (
                "pca",
                PCA(n_components=2)
            ), 
        ]
    )
    return pipeline
