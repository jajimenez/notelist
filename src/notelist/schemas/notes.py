"""Module with the note schemas."""

from typing import List

from marshmallow import ValidationError
from flask_marshmallow.fields import fields

from notelist.ma import ma
from notelist.models.tags import Tag
from notelist.models.notes import Note


INVALID_VALUE = "Invalid value."


class NoteSchema(ma.SQLAlchemyAutoSchema):
    """Note schema."""

    class Meta:
        """Note schema metadata."""

        model = Note
        fields = [
            "id", "notebook_id", "active", "title", "body", "created_ts",
            "last_modified_ts", "tags"]
        include_fk = True
        load_only = ["notebook_id"]
        dump_only = ["id", "created_ts", "last_modified_ts"]
        ordered = True
        load_instance = True

    tags = fields.Method("dump_tags", "load_tags")

    def dump_tags(self, obj: Note) -> List[str]:
        """Serialize the note's tags."""
        return sorted([t.name.strip() for t in obj.tags])

    def load_tags(self, val: List[str]) -> List[Tag]:
        """Deserialize the note's tags."""
        if (
            type(val) != list or
            any(map(lambda i: type(i) != str or not i.strip(), val))
        ):
            raise ValidationError({"tags": INVALID_VALUE})

        return [Tag(name=i.strip()) for i in val]
