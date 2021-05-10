"""Module with the note schemas."""

from notelist.ma import ma
from notelist.models.notes import Note


class NoteSchema(ma.SQLAlchemyAutoSchema):
    """Note schema."""

    class Meta:
        """Note schema metadata."""

        model = Note
        include_fk = True
        load_only = ["notebook_id"]
        dump_only = ["id", "creation_ts", "last_modification_ts"]
        ordered = True
        load_instance = True
