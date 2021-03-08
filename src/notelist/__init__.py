"""Notelist main package.

Notelist is a REST API based note taking web application.
"""

from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError

from notelist.db import db
from notelist.ma import ma
from notelist.resources import get_response_data
from notelist.resources.users import UserListResource, UserResource


__version__ = "0.1.0"

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.secret_key = "secret_key"

db.init_app(app)
ma.init_app(app)

api = Api(app)
jwt = JWTManager(app)
mig = Migrate(app, db)


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


api.add_resource(UserListResource, "/users")
api.add_resource(UserResource, "/user/<string:username>")