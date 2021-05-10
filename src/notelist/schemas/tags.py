"""Module with the tag schemas."""

from notelist.ma import ma
from notelist.models.tags import Tag


class TagSchema(ma.SQLAlchemyAutoSchema):
    """Tag schema."""

    class Meta:
        """Tag schema metadata."""

        model = Tag
        include_fk = True
        load_only = ["notebook_id"]
        dump_only = ["id"]
        ordered = True
        load_instance = True
