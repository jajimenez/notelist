"""Module with the database notebook models."""

from notelist.db import db
from notelist.tools import generate_uuid, get_current_ts


class Notebook(db.Model):
    """Database Notebook model."""

    __tablename__ = "notebooks"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_ts = db.Column(db.Integer, nullable=False, default=get_current_ts)
    last_modified_ts = db.Column(
        db.Integer, nullable=False, default=get_current_ts)

    tags = db.relationship(
        "Tag", backref="notebook", cascade_backrefs="all, delete", lazy=True)
    notes = db.relationship(
        "Note", backref="notebook", cascade_backrefs="all, delete", lazy=True)

    # Constraint: 2 or more notebooks of the same user can't have the same name
    __table_args__ = (
        db.UniqueConstraint(user_id, name, name="un_notebooks_uid_name"),)

    @classmethod
    def get_all(cls, user_id: str) -> list["Notebook"]:
        """Return all the notebooks of a user.

        :param user_id: User ID.
        :return: List of `Notebook` instances.
        """
        return (
            cls.query.filter_by(user_id=user_id).order_by(Notebook.name).all())

    @classmethod
    def get_by_id(cls, _id: str) -> "Notebook":
        """Return a notebook given its ID.

        :param _id: Notebook ID.
        :return: `Notebook` instance.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_by_name(cls, user_id: str, name: str) -> "Notebook":
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
