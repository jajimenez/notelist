"""Module with the database tag models."""

from typing import List
from notelist.db import db


class Tag(db.Model):
    """Database Tag model."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    notebook_id = db.Column(
        db.Integer, db.ForeignKey("notebooks.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # HTML (e.g. "#ffffff" or "ffffff")
    color = db.Column(db.String(7), nullable=True)

    # Constraint: A notebook can't have 2 or more tags with the same name
    __table_args__ = (
        db.UniqueConstraint(notebook_id, name, name="un_tags_nid_name"),)

    @classmethod
    def get_by_id(cls, _id: int) -> "Tag":
        """Return a tag given its ID.

        :param _id: Tag ID.
        :return: `Tag` instance.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_by_name(cls, notebook_id: int, name: str) -> "Tag":
        """Return a tag given the notebook ID and the tag name.

        :param notebook_id: Notebook ID.
        :param name: Tag name.
        :return: `Tag` instance.
        """
        return cls.query.filter_by(notebook_id=notebook_id, name=name).first()

    def save(self):
        """Save the tag."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the tag."""
        db.session.delete(self)
        db.session.commit()
