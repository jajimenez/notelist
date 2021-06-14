"""Module with the database user models."""

from notelist.db import db
from notelist.tools import generate_uuid, get_current_ts


MIN_PASSWORD = 8
MAX_PASSWORD = 100


class User(db.Model):
    """Database User model."""

    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    notebooks = db.relationship(
        "Notebook", backref="user", cascade_backrefs="all, delete", lazy=True)
    created_ts = db.Column(db.Integer, nullable=False, default=get_current_ts)
    last_modified_ts = db.Column(
        db.Integer, nullable=False, default=get_current_ts)

    @classmethod
    def get_all(cls) -> list["User"]:
        """Return all the users.

        :return: List of `User` instances.
        """
        return cls.query.order_by(User.username).all()

    @classmethod
    def get_by_id(cls, _id: str) -> "User":
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
