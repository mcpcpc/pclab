#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.decomposition import IncrementalPCA


def create_model() -> IncrementalPCA:
    return IncrementalPCA(n_components=2)
