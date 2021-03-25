"""Common logic for the tests."""

import os
import unittest
import tempfile
import random

import paths
from notelist import tools
from notelist.app import before_first_request, app
from notelist.models.users import User


class BaseTestCase(unittest.TestCase):
    """Base unit test."""

    def setUp(self):
        """Set up each unit test."""
        self.fd, self.path = tempfile.mkstemp()
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.path}"
        app.config["TESTING"] = True
        self.client = app.test_client()

        # Change the password of the "admin" user
        self.admin_username = "admin"
        self.admin_password = str(random.randint(0, 9999))  # Random password

        with app.app_context():
            before_first_request()  # Initialize database
            user = User.query.filter_by(username=self.admin_username).first()
            user.password = tools.get_hash(self.admin_password)
            user.save()

    def tearDown(self):
        """Close each unit test."""
        os.close(self.fd)
        os.remove(self.path)

        self.fd = None
        self.path = None
        self.admin_username = None
        self.admin_password = None
