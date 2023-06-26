#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request

from pclab.db import get_db

project = Blueprint(
    "project",
    __name__,
    url_prefix="/api"
)


@project.post("/project")
def create_project():
    form = request.form.copy().to_dict()
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO project (
                slug,
                title
            ) VALUES (:slug, :title)
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Project successfully created.", 201


@project.get("/project/<id:int>")
def read_project(id: int):
    row = get_db().execute(
        "SELECT * FROM project WHERE id = ?",
        (id,),
    ).fetchone()
    if not row:
        return "Project does not exist.", 404
    return dict(row), 200


@project.update("/project/<id:int>")
def update_project(id: int):
    form = request.form.copy().to_dict()
    form["id"] = id
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE project SET
                updated_at = CURRENT_TIMESTAMP,
                slug = :slug,
                title = :title
            WHERE id = :id
            """,
            form,
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Project successfully updated.", 201


@project.delete("/project/<id:int>")
def delete_project(id: int):
    db = get_db()
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("DELETE FROM project WHERE id = ?", (id,))
    db.commit()
    return "Project successfully deleted.", 200


@project.get("/project")
def list_projects():
    rows = get_db().execute("SELECT * FROM project").fetchall()
    if not rows:
        return "Projects do not exist.", 404
    return list(map(dict, rows)), 200
