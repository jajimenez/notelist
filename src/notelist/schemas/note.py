"""Module with the note schemas."""

from notelist.ma import ma
from notelist.models.notes import Note


class NoteSchema(ma.SQLAlchemyAutoSchema):
    """Note schema."""

    class Meta:
        """Note schema metadata."""

        model = Note
        ordered = True
        load_instance = True
