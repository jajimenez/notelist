"""Module with the database note models."""

from notelist.db import db


# Many-to-Many relationship between notes and tags.
#
# A note should be associated to a tag only if they both belong to the same
# notebook. We can't define this constraint here but we control it in the API
# resources (notelist.resources).
note_tags = db.Table(
    "note_tags",

    db.Column("id", db.Integer, primary_key=True),
    db.Column(
        "note_id", db.Integer, db.ForeignKey("notes.id"), nullable=False),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), nullable=False),

    db.UniqueConstraint("note_id", "tag_id", name="un_note_id_tag_id"))


class Note(db.Model):
    """Database Note model."""

    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    notebook_id = db.Column(
        db.Integer, db.ForeignKey("notebooks.id"), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    title = db.Column(db.String(100), nullable=True)
    body = db.Column(db.String(1000), nullable=True)
    creation_ts = db.Column(db.Integer, nullable=True)
    last_modification_ts = db.Column(db.Integer, nullable=True)

    tags = db.relationship(
        "Tag", secondary=note_tags, lazy="subquery",
        backref=db.backref("notes", lazy=True))
