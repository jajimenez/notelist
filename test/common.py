"""Common logic for the tests."""

import os
import unittest
import tempfile
import random

import paths
from notelist.app import app
from notelist import tools
from notelist.models.users import User


class BaseTestCase(unittest.TestCase):
    """Base unit test."""

    def setUp(self):
        """Set up each unit test."""
        self.db_fd, app.config["DATABASE"] = tempfile.mkstemp()
        app.config["TESTING"] = True
        self.client = app.test_client()

        # Making any request will call the "app.before_first_request" function
        self.client.get("/")

        # Change the password of the "admin" user
        self.admin_username = "admin"
        self.admin_password = str(random.randint(0, 9999))  # Random password

        with app.app_context():
            user = User.query.first()
            user.password = tools.get_hash(self.admin_password)
            user.save()

    def tearDown(self):
        """Close each unit test."""
        os.close(self.db_fd)
        os.unlink(app.config["DATABASE"])

        self.db_fd = None
        self.client = None
