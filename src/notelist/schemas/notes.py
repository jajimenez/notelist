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

    title = fields.Method("dump_title", "load_title")
    tags = fields.Method("dump_tags", "load_tags")

    def dump_title(self, obj: Note) -> str:
        """Serialize the note's title."""
        return obj.title.strip() if obj.title else obj.title

    def load_title(self, val: str) -> str:
        """Deserialize the note's title."""
        if val is not None and type(val) != str:
            raise ValidationError({"title": INVALID_VALUE})

        return val.strip() if val else val

    def dump_tags(self, obj: Note) -> List[str]:
        """Serialize the note's tags."""
        return [t.name.strip() for t in obj.tags]

    def load_tags(self, val: List[str]) -> List[Tag]:
        """Deserialize the note's tags."""
        if (
            type(val) != list or
            any(map(lambda i: type(i) != str or not i.strip(), val))
        ):
            raise ValidationError({"tags": INVALID_VALUE})

        return [Tag(name=i.strip()) for i in val]
