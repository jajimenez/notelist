"""Module with the database tag models."""

from typing import List
from notelist.db import db


class Tag(db.Model):
    """Database User model."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7))
    notebook_id = db.Column(
        db.Integer, db.ForeignKey("notebooks.id"), nullable=False)
    notebook = db.relationship("Notebook", cascade="all, delete")

    # Constraint: A notebook can't have 2 or more tags with the same name
    __table_args__ = (
        db.UniqueConstraint(notebook_id, name), name="un_tags_nid_name",)

    @classmethod
    def get_all(cls, notebook_id: int) -> List["Tag"]:
        """Return all the tags from the database of a given notebook.

        :param notebook_id: Notebook ID.
        :return: List of `Tag` instances.
        """
        return cls.query.filter_by(notebook_id=notebook_id).all()

    @classmethod
    def get_by_id(cls, _id: int) -> "Tag":
        """Return a tag from the database given the tag ID.

        :param _id: Tag ID.
        :return: `Tag` instance.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_by_name(cls, notebook_id: int, name: str) -> "Tag":
        """Return a tag from the database given the notebook ID and the tag
        name.

        :param notebook_id: Notebook ID.
        :param name: Tag name.
        :return: `Tag` instance.
        """
        return cls.query.filter_by(notebook_id=notebook_id, name=name).first()

    def save(self):
        """Save the tag to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the tag from the database."""
        db.session.delete(self)
        db.session.commit()
