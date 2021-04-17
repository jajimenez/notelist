"""Common logic for the tests."""

import os
import unittest
import tempfile
import random

import paths
from notelist import tools
from notelist.app import app, init_db
from notelist.models.users import User


class BaseTestCase(unittest.TestCase):
    """Base unit test."""

    def setUp(self):
        """Set up each unit test."""
        # Create a temporary file to store the database (SQLite)
        self.fd, self.path = tempfile.mkstemp()

        # Set up the API
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.path}"
        app.config["TESTING"] = True

        # Initial password of the "root" user
        self.root_password = str(random.randint(0, 99999999))  # Random number

        # Test API client
        self.client = app.test_client()

        # Initialize the database
        with app.app_context():
            init_db(self.root_password)

    def tearDown(self):
        """Close each unit test."""
        # Close and delete the temporary database file
        os.close(self.fd)
        os.remove(self.path)

        self.fd = None
        self.path = None
        self.root_password = None
