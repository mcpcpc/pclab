-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS label;
DROP TABLE IF EXISTS sample;

CREATE TABLE label (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL
);

INSERT INTO label (slug, title) VALUES
    ("normal", "Normal"),
    ("anomaly", "Anomaly");

CREATE TABLE sample (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    blob BINARY UNIQUE NOT NULL,
    label_id INTEGER DEFAULT 1,
    FOREIGN KEY(label_id) REFERENCES label(id) ON DELETE CASCADE ON UPDATE NO ACTION
);
