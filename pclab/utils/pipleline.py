#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.decomposition import PCA


def create_model() -> PCA:
    return PCA(n_components=2)
