"""Module with the database tag models."""

from notelist.db import db
from notelist.tools import generate_uuid, get_current_ts


class Tag(db.Model):
    """Database Tag model."""

    __tablename__ = "tags"

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    notebook_id = db.Column(
        db.String(36), db.ForeignKey("notebooks.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=True)  # HTML (e.g. "#ffffff")
    created_ts = db.Column(db.Integer, nullable=False, default=get_current_ts)
    last_modified_ts = db.Column(
        db.Integer, nullable=False, default=get_current_ts)

    # Constraint: A notebook can't have 2 or more tags with the same name
    __table_args__ = (
        db.UniqueConstraint(notebook_id, name, name="un_tags_nid_name"),)

    @classmethod
    def get_by_id(cls, _id: str) -> "Tag":
        """Return a tag given its ID.

        :param _id: Tag ID.
        :return: `Tag` instance.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_by_name(cls, notebook_id: str, name: str) -> "Tag":
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
