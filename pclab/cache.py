#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from dash import CeleryManager
from dash import DiskcacheManager
from diskcache import Cache
from celery import Celery


def create_cache_manager(app):
    if isinstance(app.config.get("REDIS_URL"), str):
        celery_app = Celery(
            __name__,
            broker=app.config.get("REDIS_URL"),
            backend=app.config.get("REDIS_URL"),
        )
        manager = CeleryManager(celery_app)
    else:
        cache = Cache(path.join(app.instance_path, ".cache"))
        manager = DiskcacheManager(cache)
    return manager