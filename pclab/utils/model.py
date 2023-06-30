#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from sklearn.decomposition import PCA
from sklearn.decomposition import IncrementalPCA

#def create_model() -> PCA:
    #return PCA(n_components=2, random_state=0)
def create_model() -> IncrementalPCA: 
    return IncrementalPCA(n_components=2)