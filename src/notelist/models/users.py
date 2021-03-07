"""Module with the database user models."""

from typing import List
from db import db


class User(db.Model):
    """Database User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    @classmethod
    def get_all(cls) -> List["UserModel"]:
        """Return all the users from the database.

        :return: List of `UserModel` instances.
        """
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id: str) -> "UserModel":
        """Return a user from the database given the user ID.

        :param id: User ID.
        :return: `UserModel` instance.
        """
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_username(cls, username: str) -> "UserModel":
        """Return a user from the database given the username.

        :param id: Username.
        :return: `UserModel` instance.
        """
        return cls.query.filter_by(username=username).first()

    def save(self):
        """Save the user to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the user to the database."""
        db.session.delete(self)
        db.session.commit()
