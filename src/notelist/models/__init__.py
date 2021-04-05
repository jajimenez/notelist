"""Package with the database models."""

# We need to import the models in the "__init__" file as otherwise we would get
# an error when defining relationships between models with "db.relationship".
from notelist.models.users import User
from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.models.notes import Note
