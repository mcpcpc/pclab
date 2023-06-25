#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import BytesIO

from flask import Blueprint
from flask import request
from flask import send_file
from werkzeug.utils import secure_filename

from pclab.db import get_db

sample = Blueprint(
    "sample",
    __name__,
    url_prefix="/api"
)


@sample.post("/sample")
def create_sample():
    file = request.files.get("file")
    filename = secure_filename(file.filename)
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            INSERT INTO sample (
                filename,
                blob
            ) VALUES (?, ?)
            """,
            (filename, file.stream),
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Invalid parameter(s).", 400
    return "Sample successfully created.", 201


@sample.get("/sample/<int:id>")
def read_sample(id: int):
    row = get_db().execute(
        "SELECT * FROM sample WHERE id = ?",
        (id,),
    ).fetchone()
    if not row:
        return "sample does not exist.", 404
    return send_file(
        BytesIO(dict(row)["blob"]),
        download_name=dict(row)["filename"],
        as_attachment=True,
    )


@sample.put("/sample/<int:id>")
def update_sample(id: int):
    file = request.files("file")
    filename = secure_filename(file.filename)
    try:
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON")
        db.execute(
            """
            UPDATE sample set
                updated_at = CURRENT_TIMESTAMP,
                filename = ?,
                blob = ?
            WHERE id = ?
            """,
            (filename, file.stream, id),
        )
        db.commit()
    except db.ProgrammingError:
        return "Missing parameter(s).", 400
    except db.IntegrityError:
        return "Sample successfully updated.", 201
    return "sample successfully updated.", 201


@sample.delete("/sample/<int:id>")
def delete_sample(id: int):
    db = get_db()
    db.execute("PRAGMA foreign_keys = ON")
    db.execute(
        "DELETE FROM sample WHERE id = ?",
        (id,)
    )
    db.commit()
    return "Sample successfully deleted.", 200


@sample.get("/sample")
def list_samples():
    rows = get_db().execute(
        """SELECT id, filename, label_id FROM sample"""
    ).fetchall()
    if not rows:
        return "Samples do not exist.", 404
    return list(map(dict, rows)), 200