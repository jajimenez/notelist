"""Notelist package.

Notelist is a note taking REST API.
"""

import os
from os.path import dirname, join
from typing import Optional, Union, List, Dict

import click
from flask import Flask, Blueprint, render_template
from flask.cli import AppGroup
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError

from notelist import tools
from notelist.db import db
from notelist.ma import ma
from notelist.apis import (
    auth_api, users_api, notebooks_api, tags_api, notes_api, search_api)
from notelist.resources import get_response_data, Response
from notelist.resources.users import (
    LoginResource, TokenRefreshResource, LogoutResource, UserListResource,
    NewUserResource, ExistingUserResource, blocklist)
from notelist.resources.notebooks import (
    NotebookListResource, NewNotebookResource, ExistingNotebookResource)
from notelist.resources.tags import (
    TagListResource, NewTagResource, ExistingTagResource)
from notelist.resources.notes import (
    NoteListResource, NewNoteResource, ExistingNoteResource)
from notelist.resources.search import SearchResource
from notelist.models.users import User


__version__ = "0.1.0"

API_NAME = "Notelist"
API_DESC = "Note taking REST API"

# Typing types
ValErrorData = Dict[str, List[str]]
JwtData = Dict[str, Union[int, str]]

# Environment variables
SECRET_KEY = "NOTELIST_SECRET_KEY"
DB_URI = "NOTELIST_DB_URI"

# Texts
VALIDATION_ERROR = "Validation error: {}."
ACCESS_TOKEN_MISSING = "Access token missing."
FRESH_ACCESS_TOKEN_REQ = "Fresh access token required."
EXPIRED_TOKEN = "Expired token."
REVOKED_TOKEN = "Revoked token."
INVALID_ACCESS_TOKEN = "Invalid access token."

# Application setup
app = Flask(__name__)
app.config["DEBUG"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(DB_URI)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

# The Secret Key is used for storing session information specific to a user
# from one request to the next. This is implemented on top of cookies which are
# signed cryptographically with the secret key. This means that the user could
# look at the contents of the cookies but not modify it unless they knew the
# secret key. A secret key should be as random as possible.
app.secret_key = os.environ.get(SECRET_KEY)

# Database
db.init_app(app)
ma.init_app(app)
mig = Migrate(app, db)

# API
blue = Blueprint("notelist", __name__, url_prefix="/")
auth = {"apikey": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(blue, __version__, API_NAME, API_DESC, authorizations=auth)
api.add_namespace(auth_api)
api.add_namespace(users_api)
api.add_namespace(notebooks_api)
api.add_namespace(tags_api)
api.add_namespace(notes_api)
api.add_namespace(search_api)

app.register_blueprint(blue)

# User authentication
jwt = JWTManager(app)

# Flask commands
path_cli = AppGroup("path")
user_cli = AppGroup("user")

app.cli.add_command(path_cli)
app.cli.add_command(user_cli)


@path_cli.command("migrations")
def print_migrations_path():
    """Print the migrations directory full path."""
    print(join(dirname(__file__), "migrations"))


@user_cli.command("create")
@click.argument("username", type=str)
@click.argument("password", type=str)
@click.argument("admin", type=bool)
@click.argument("enabled", type=bool)
@click.argument("name", type=str, required=False)
@click.argument("email", type=str, required=False)
def create_user(
    username: str, password: str, admin: bool, enabled: bool,
    name: Optional[str] = None, email: Optional[str] = None
):
    """Create a user in the database.

    :param username: Username.
    :param password: Password.
    :param admin: Whether the user is an administrator or not.
    :param enabled: Whether the user is enabled or not.
    :param name: Name (optional).
    :param email: E-mail address (optional).
    """
    password = tools.get_hash(password)  # Encrypt password
    user = User(
        username=username, password=password, admin=admin, enabled=enabled,
        name=name, email=email)

    user.save()
    print("User created.")


@app.errorhandler(ValidationError)
def validation_error_handler(error: ValErrorData) -> Response:
    """Handle validation errors (callback function).

    :param error: Object containing the error messages.
    :return: Dictionary containing the error message.
    """
    fields = ", ".join([i for i in error.messages.keys()])
    return get_response_data(VALIDATION_ERROR.format(fields)), 400


@jwt.unauthorized_loader
def unauthorized_loader(error: str) -> Response:
    """Handle requests with no JWT.

    :param error: Error message.
    :return: Dictionary containing the error message.
    """
    return get_response_data(ACCESS_TOKEN_MISSING), 401


@jwt.needs_fresh_token_loader
def needs_fresh_token_loader(header: JwtData, payload: JwtData) -> Response:
    """Handle requests with a not fresh JWT.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Dictionary containing the error message.
    """
    return get_response_data(FRESH_ACCESS_TOKEN_REQ), 401


@jwt.expired_token_loader
def expired_token_loader(header: JwtData, payload: JwtData) -> Response:
    """Handle requests with an expired JWT.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Dictionary containing the error message.
    """
    return get_response_data(EXPIRED_TOKEN), 401


@jwt.revoked_token_loader
def revoked_token_loader(header: JwtData, payload: JwtData) -> Response:
    """Handle requests with a revoked JWT.

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Dictionary containing the error message.
    """
    return get_response_data(REVOKED_TOKEN), 401


@jwt.invalid_token_loader
def invalid_token_loader(error: str) -> Response:
    """Handle requests with an invalid JWT.

    :param error: Error message.
    :return: Dictionary containing the error message.
    """
    return get_response_data(INVALID_ACCESS_TOKEN), 422


@jwt.token_in_blocklist_loader
def blocklist_loader(header: JwtData, payload: JwtData) -> bool:
    """Check if a JWT has been revoked (callback function).

    :param header: JWT header data.
    :param payload: JWT payload data.
    :return: Whether the given JWT has been revoked or not.
    """
    return payload["jti"] in blocklist


@jwt.additional_claims_loader
def additional_claims_loader(identity) -> Dict[str, bool]:
    """Add additional information to the JWT payload when creating a JWT.

    :param identity: JWT identity. In this case, it's the user ID.
    :return: Dictionary with additional information about the request user.
    """
    user = User.get_by_id(identity)
    return {"user_id": user.id, "admin": user.admin}
