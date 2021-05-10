"""Module with the database notebook models."""

from typing import List
from notelist.db import db


class Notebook(db.Model):
    """Database Notebook model."""

    __tablename__ = "notebooks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    tags = db.relationship(
        "Tag", backref="notebook", cascade_backrefs="all, delete", lazy=True)
    notes = db.relationship(
        "Note", backref="notebook", cascade_backrefs="all, delete", lazy=True)

    # Constraint: 2 or more notebooks of the same user can't have the same name
    __table_args__ = (
        db.UniqueConstraint(user_id, name, name="un_notebooks_uid_name"),)

    @classmethod
    def get_all(cls, user_id: int) -> List["Notebook"]:
        """Return all the notebooks of a user.

        :param user_id: User ID.
        :return: List of `Notebook` instances.
        """
        return cls.query.filter_by(user_id=user_id).order_by(Notebook.id).all()

    @classmethod
    def get_by_id(cls, _id: int) -> "Notebook":
        """Return a notebook given its ID.

        :param _id: Notebook ID.
        :return: `Notebook` instance.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_by_name(cls, user_id: int, name: str) -> "Notebook":
        """Return a notebook given the user ID and the notebook name.

        :param user_id: User ID.
        :param name: Notebook name.
        :return: `Notebook` instance.
        """
        return cls.query.filter_by(user_id=user_id, name=name).first()

    def save(self):
        """Save the notebook."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the notebook."""
        db.session.delete(self)
        db.session.commit()
