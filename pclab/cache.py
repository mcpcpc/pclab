#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from uuid import uuid4

from dash import CeleryManager
from dash import DiskcacheManager
from diskcache import Cache
from celery import Celery

launch_uid = uuid4()


def create_cache_manager(app):
    if isinstance(app.config.get("REDIS_URL"), str):
        celery_app = Celery(
            __name__,
            broker=app.config.get("REDIS_URL"),
            backend=app.config.get("REDIS_URL"),
            cache_by=[lambda: launch_uid],
            expire=60,
        )
        manager = CeleryManager(celery_app)
    else:
        cache = Cache(
            path.join(app.instance_path, ".cache")
            cache_by=[lambda: launch_uid],
            expire=60,
        )
        manager = DiskcacheManager(cache)
    return manager