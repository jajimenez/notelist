"""Application module."""

import os

from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError

from notelist.db import db
from notelist.ma import ma
from notelist.resources import get_response_data
from notelist.resources.users import UserListResource, UserResource


# Application setup
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

# The Secret Key is used for storing session information specific to a user
# from one request to the next. This is implemented on top of cookies which are
# signed cryptographically with the Secret Key. This means that the user could
# look at the contents of the cookies but not modify it unless they knew the
# Secret Key. A secret key should be as random as possible.
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
def create_tables():
    """Create all the datatabase tables."""
    db.create_all()


@app.errorhandler(ValidationError)
def validation_error(e):
    """Handle validation errors."""
    fields = ", ".join([i for i in e.messages.keys()])
    return get_response_data(f"Validation error: {fields}."), 400


@app.route("/")
def home():
    """Root route request handler."""
    return render_template("home.html")


def run():
    """Run the application."""
    app.run(port=5000, debug=True)
