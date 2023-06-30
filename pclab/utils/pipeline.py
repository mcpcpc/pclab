#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.decomposition import IncrementalPCA
from sklearn.pipeline import Pipeline


def create_pipeline() -> IncrementalPCA:
    pipeline = Pipeline(
        steps=[
            (
                "incremental_pca",
                IncrementalPCA(n_components=2)
            ), 
        ]
    )
    return pipeline
