"""Module with the user schemas."""

from ma import ma
from models.users import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    """User schema."""

    class Meta:
        """User schema metadata."""

        model = User
        load_only = ("password",)
        ordered = True
        load_instance = True
