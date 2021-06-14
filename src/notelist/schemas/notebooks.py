"""Module with the notebook schemas."""

from notelist.ma import ma
from notelist.models.notebooks import Notebook


class NotebookSchema(ma.SQLAlchemyAutoSchema):
    """Notebook schema."""

    class Meta:
        """Notebook schema metadata."""

        model = Notebook
        dump_only = ["id", "created_ts", "last_modified_ts"]
        ordered = True
        load_instance = True
