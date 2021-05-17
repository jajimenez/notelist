"""Module with the database user models."""

from typing import List
from notelist.db import db


MIN_PASSWORD = 8
MAX_PASSWORD = 100


class User(db.Model):
    """Database User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    notebooks = db.relationship(
        "Notebook", backref="user", cascade_backrefs="all, delete", lazy=True)

    @classmethod
    def get_all(cls) -> List["User"]:
        """Return all the users.

        :return: List of `User` instances.
        """
        return cls.query.order_by(User.id).all()

    @classmethod
    def get_by_id(cls, _id: int) -> "User":
        """Return a user given its ID.

        :param _id: User ID.
        :return: `User` instance.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_by_username(cls, username: str) -> "User":
        """Return a user given its username.

        :param id: Username.
        :return: `User` instance.
        """
        return cls.query.filter_by(username=username).first()

    def save(self):
        """Save the user."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the user."""
        db.session.delete(self)
        db.session.commit()
