"""Module with the API namespace objects."""

from flask_restx import Namespace


auth_api = Namespace("authentication", "User authentication resources", "/")
users_api = Namespace("users", "User resources", "/")
notebooks_api = Namespace("notebooks", "Notebook resources", "/")
tags_api = Namespace("tags", "Tag resources", "/")
notes_api = Namespace("notes", "Note resources", "/")
search_api = Namespace("search", "Search resources", "/")
