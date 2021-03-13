"""Application module."""

import os
from typing import List, Dict, Union

from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError

import notelist.config as conf
from notelist.db import db
from notelist.ma import ma
from notelist.resources import get_response_data, Response
from notelist.resources.users import (
    UserListResource, UserResource, LoginResource, TokenRefreshResource,
    LogoutResource, blocklist)
from notelist.models.users import User


# Typing types
ValErrorData = Dict[str, List[str]]
JwtData = Dict[str, Union[int, str]]

# Constants
VALIDATION_ERROR = "Validation error: {}."
ACCESS_TOKEN_MISSING = "Access token missing."
FRESH_ACCESS_TOKEN_REQ = "Fresh access token required."
INVALID_ACCESS_TOKEN = "Invalid access token."
CONF_NOT_SET = (
    'Configuration parameters not defined.\nRun "notelist configure" to set '
    'the parameters.')

# Application setup
app = Flask(__name__)
app.config["DEBUG"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Temporal URI
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

# Resources
api = Api(app)
api.add_resource(UserListResource, "/users")
api.add_resource(UserResource, "/user/<string:username>")
api.add_resource(LoginResource, "/login")
api.add_resource(TokenRefreshResource, "/refresh")
api.add_resource(LogoutResource, "/logout")

# User login
jwt = JWTManager(app)


@app.before_first_request
def before_first_request():
    """Create all the datatabase tables (callback function).

    This method is called before accessing the database for the first time. It
    creates the administrator user ("admin") if it doesn't exist, with an
    initial password.
    """
    # Create tables
    db.create_all()

    # Create the administrator user
    if not User.get_by_username("admin"):
        User(
            username="admin", password=conf.get_config()[3], enabled=True,
            admin=True, name="Administrator"
        ).save()


@app.errorhandler(ValidationError)
def validation_error_handler(error: ValErrorData) -> Response:
    """Handle validation errors (callback function).

    :param error: Object containing the error messages.
    :return: Dictionary containing the error message.
    """
    fields = ", ".join([i for i in e.messages.keys()])
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

    :return: Dictionary containing the error message.
    """
    return get_response_data(FRESH_ACCESS_TOKEN_REQ), 401


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

    :param header: Header data of the JWT.
    :param payload: Payload data of the JWT.
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
    return {"username": user.username, "admin": user.admin}


@app.route("/")
def home() -> str:
    """Root route request handler."""
    return render_template("home.html")


def run():
    """Run the application."""
    host, port, db_uri, _ = conf.get_config()

    if host and port and db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
        app.run(host=host, port=port, debug=False)
    else:
        print(CONF_NOT_SET)
