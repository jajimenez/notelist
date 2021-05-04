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
        """Initialize each unit test."""
        # Create a temporary file to store the database (SQLite)
        self.fd, self.path = tempfile.mkstemp()

        # Set up the API
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.path}"
        app.config["TESTING"] = True
        app.secret_key = str(random.randint(0, 9999))

        # Test API client
        self.client = app.test_client()

        # Initialize database
        with app.app_context():
            # Create database tables
            db.create_all()

            # Create an administrator user
            self.admin = {
                "username": "root",
                "password": str(random.randint(0, 99999999)),
                "name": "Root"}

            u = User(
                username=self.admin["username"],
                password=tools.get_hash(self.admin["password"]), admin=True,
                enabled=True, name=self.admin["name"], email=None)

            u.save()
            self.admin["id"] = u.id

            # Create a regular (not administrator) user
            self.reg1 = {
                "username": "reg_user_1",
                "password": str(random.randint(0, 99999999)),
                "name": "Regular User 1"}

            u = User(
                username=self.reg1["username"],
                password=tools.get_hash(self.reg1["password"]), admin=False,
                enabled=True, name=self.reg1["name"], email=None)

            u.save()
            self.reg1["id"] = u.id

            # Create a regular, disabled, user.
            self.reg2 = {
                "username": "reg_user_2",
                "password": str(random.randint(0, 99999999)),
                "name": "Regular User 2"}

            u = User(
                username=self.reg2["username"],
                password=tools.get_hash(self.reg2["password"]), admin=False,
                enabled=False, name=self.reg2["name"], email=None)

            u.save()
            self.reg2["id"] = u.id

    def tearDown(self):
        """Close each unit test."""
        # Close and delete the temporary database file
        os.close(self.fd)
        os.remove(self.path)

        self.fd = None
        self.path = None

        self.admin_username = None
        self.admin_password = None
        self.reg_username_1 = None
        self.reg_password_1 = None
        self.reg_username_2 = None
        self.reg_password_2 = None
