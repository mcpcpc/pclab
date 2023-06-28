#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlite3 import connect
from sqlite3 import PARSE_DECLTYPES
from sqlite3 import Row

from click import command
from click import echo
from flask import current_app
from flask import g


def get_db():
    if "db" not in g:
        g.db = connect(
            current_app.config["DATABASE"],
            detect_types=PARSE_DECLTYPES,
        )
        g.db.row_factory = Row
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as file:
        db.executescript(file.read().decode("utf8"))


@command("init-db")
def init_db_command():
    init_db()
    echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
