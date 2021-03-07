"""Module with the database object."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


db = SQLAlchemy(metadata=MetaData())
