#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from os import makedirs

from flask import Flask
from dash import Dash
from dash import page_registry

from pclab.api.sample import sample
from pclab.cache import create_cache_manager
from pclab.db import init_app
from pclab.layout.default import layout

__version__ = "0.0.1"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        MAX_CONTENT_LENGTH=16 * 1000 * 1000,
        DATABASE=path.join(app.instance_path, "pclab.sqlite"),
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)
    try:
        makedirs(app.instance_path)
    except OSError:
        pass
    init_app(app)
    app.register_blueprint(sample)
    manager = create_cache_manager(app)
    dashapp = Dash(
        __name__,
        server=app,
        use_pages=True,
        update_title=None,
        background_callback_manager=manager,
    )
    dashapp.layout = layout()
    return dashapp.server
