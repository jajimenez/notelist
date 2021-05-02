"""Common logic for the tests."""

import os
import unittest
import tempfile
import random

import paths
from notelist import app, db, tools
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

        # Test API client
        self.client = app.test_client()

        # Initialize database
        with app.app_context():
            # Create database tables
            db.create_all()

            # Create administrator user
            self.admin_username = "root"
            self.admin_password = str(random.randint(0, 99999999))

            User(
                username=self.admin_username,
                password=tools.get_hash(self.admin_password), admin=True,
                enabled=True, name=None, email=None).save()

    def tearDown(self):
        """Close each unit test."""
        # Close and delete the temporary database file
        os.close(self.fd)
        os.remove(self.path)

        self.fd = None
        self.path = None
        self.admin_username = None
        self.admin_password = None
