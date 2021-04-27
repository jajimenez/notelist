"""Application module."""

import os
from typing import Optional, Union, List, Dict

from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError

import notelist.config as conf
import notelist.tools as tools
from notelist.db import db
from notelist.ma import ma
from notelist.resources import get_response_data, Response
from notelist.resources.users import (
    LoginResource, TokenRefreshResource, LogoutResource, UserListResource,
    UserResource, blocklist)
from notelist.resources.notebooks import NotebookListResource, NotebookResource
from notelist.resources.tags import TagListResource, TagResource
from notelist.models.users import User


# Typing types
ValErrorData = Dict[str, List[str]]
JwtData = Dict[str, Union[int, str]]

# Constants
VALIDATION_ERROR = "Validation error: {}."
ACCESS_TOKEN_MISSING = "Access token missing."
FRESH_ACCESS_TOKEN_REQ = "Fresh access token required."
EXPIRED_TOKEN = "Expired token."
INVALID_ACCESS_TOKEN = "Invalid access token."
DB_URI_NOT_SET = (
    'Database URI is not set. To set it, edit the file '
    f'"{conf.get_conf_path()}".')

# Configuration:
# - Database URI
# - "root" user initial password (optional)
db_uri = conf.get_val(conf.DB_URI_KEY)
root_ip = conf.get_val(conf.ROOT_IP_KEY)

if type(db_uri) != str or not db_uri:
    raise Exception(DB_URI_NOT_SET)

# Application setup
app = Flask(__name__)
app.config["DEBUG"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

# The Secret Key is used for storing session information specific to a user
# from one request to the next. This is implemented on top of cookies which are
# signed cryptographically with the secret key. This means that the user could
# look at the contents of the cookies but not modify it unless they knew the
# secret key. A secret key should be as random as possible.
app.secret_key = os.urandom(16)  # Random value (bytes)

# Database
db.init_app(app)
ma.init_app(app)
mig = Migrate(app, db)

# Initialize database
with app.app_context():
    # Create tables if the don't exist
    db.create_all()

    # Create/update the "root" user
    if type(root_ip) == str and root_ip:
        user = User.get_by_username("root")  # Get the user (if it exists)
        password = tools.get_hash(root_ip)  # Encrypt password

        if user:
            # Update user
            user.password = password
        else:
            # Create user
            user = User(
                username="root", password=password, enabled=True, admin=True,
                name="Root")

        # Reset the "root" user initial password
        conf.set_val(conf.ROOT_IP_KEY, "")
        root_ip = None

        user.save()

# Resources
api = Api(app)
api.add_resource(LoginResource, "/login")
api.add_resource(TokenRefreshResource, "/refresh")
api.add_resource(LogoutResource, "/logout")
api.add_resource(UserListResource, "/users")
api.add_resource(UserResource, "/user", "/user/<int:user_id>")
api.add_resource(NotebookListResource, "/notebooks")
api.add_resource(NotebookResource, "/notebook", "/notebook/<int:notebook_id>")
api.add_resource(TagListResource, "/tags/<int:notebook_id>")
api.add_resource(TagResource, "/tag", "/tag/<int:tag_id>")

# User login
jwt = JWTManager(app)


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


@app.route("/")
def home() -> str:
    """Root route request handler."""
    return render_template("home.html")
