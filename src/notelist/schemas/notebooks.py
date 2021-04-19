"""Module with the notebook schemas."""

from notelist.ma import ma
from notelist.models.notebooks import Notebook


class NotebookSchema(ma.SQLAlchemyAutoSchema):
    """Notebook schema."""

    class Meta:
        """Notebook schema metadata."""

        model = Notebook
        include_fk = True
        exclude = ["user_id"]
        ordered = True
        load_instance = True
