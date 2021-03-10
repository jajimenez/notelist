"""Application module."""

import os

from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError

import notelist.config as conf
from notelist.db import db
from notelist.ma import ma
from notelist.resources import get_response_data
from notelist.resources.users import UserListResource, UserResource
from notelist.models.users import User


CONF_NOT_SET = (
    'Configuration parameters not defined.\nRun "notelist configure" to set '
    'the parameters.')

# Application setup
app = Flask(__name__)
app.config["DEBUG"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
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

# User login
jwt = JWTManager(app)


@app.before_first_request
def on_first_request():
    """Create all the datatabase tables."""
    db.create_all()

    # Create the administrator user ("admin") if it doesn't exist, with an
    # initial password.
    if not User.get_by_username("admin"):
        User(
            username="admin", password=conf.get_config()[3], enabled=True,
            admin=True, name="Administrator"
        ).save()


@app.errorhandler(ValidationError)
def on_validation_error(e):
    """Handle validation errors."""
    fields = ", ".join([i for i in e.messages.keys()])
    return get_response_data(f"Validation error: {fields}."), 400


@app.route("/")
def home():
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
