"""Module with the user schemas."""

from notelist.ma import ma
from notelist.models.users import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """User schema."""

    class Meta:
        """User schema metadata."""

        model = User
        load_only = ("password",)
        ordered = True
        load_instance = True
