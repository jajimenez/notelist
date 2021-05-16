"""Module with the database note models."""

from typing import List, Optional
from sqlalchemy import desc

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
    created_ts = db.Column(db.Integer, nullable=True)
    last_modified_ts = db.Column(db.Integer, nullable=True)

    tags = db.relationship(
        "Tag", secondary=note_tags, lazy="subquery",
        backref=db.backref("notes", lazy=True))

    @classmethod
    def get_by_filter(
        cls, notebook_id: int, active: Optional[bool] = None,
        tags: Optional[List[str]] = None, no_tags: bool = False,
        last_mod: bool = False, asc: bool = True
    ) -> List["Note"]:
        """Return all the notes of a notebook by a filter.

        :param notebook_id: Notebook ID.
        :param active: State filter (include active notes or not active notes).
        :param tags: Tags filter (include notes that has any of these tags).
        This list contains tag names.
        :param no_tags: Notes with No Tags filter (include notes with no tags).
        This filter is only applicable if a tag filter has been provided, i.e.
        `tags` is not None).
        :param last_mod: `True` if notes should be sorted by their Last
        Modified timestamp. `False` if notes should be sorted by their Created
        timestamp (default).
        :param asc: Whether the notes order should be ascending (default) or
        not.
        :return: List of `Note` instances.
        """
        notes = cls.query.filter_by(notebook_id=notebook_id)

        # State filter
        if active:
            notes = notes.filter_by(active=True)
        elif active is not None:
            notes = notes.filter_by(active=False)

        # Order
        if last_mod and asc:
            notes = notes.order_by(Note.last_modified_ts).all()
        elif last_mod and not asc:
            notes = notes.order_by(desc(Note.last_modified_ts)).all()
        elif not last_mod and asc:
            notes = notes.order_by(Note.created_ts).all()
        else:
            notes = notes.order_by(desc(Note.created_ts)).all()

        # Tags and Not Tags filters
        def select_note(n: "Note") -> bool:
            """Return whether a note should be included or not based on its
            tags.

            :param n: Note.
            :return: `True` if `n` should be included. `False` otherwise.
            """
            note_tags = [t.name for t in n.tags]

            return (
                (no_tags and len(note_tags) == 0) or
                any(map(lambda t: t in note_tags, tags)))

        return notes if tags is None else list(filter(select_note, notes))

    @classmethod
    def get(cls, _id: int) -> "Note":
        """Return a note given its ID.

        :param _id: Note ID.
        :return: `Note` instance.
        """
        return cls.query.filter_by(id=_id).first()

    def save(self):
        """Save the note."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the note."""
        db.session.delete(self)
        db.session.commit()
