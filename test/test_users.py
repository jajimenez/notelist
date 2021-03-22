"""User unit tests."""

import unittest
from flask.wrappers import Response

import common
from notelist.app import app
from notelist.models.users import User


class UserTestCase(common.BaseTestCase):
    """User unit tests."""

    def _login(self, username, password) -> Response:
        """Log in given a username and a password.

        :param username: Username.
        :param password: User password.
        :return: Response.
        """
        data = {"username": username, "password": password}
        return self.client.post("/login", json=data)

    def _logout(self, access_token) -> Response:
        """Log out given an access token.

        :param access_token: Access token.
        :return: Response.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        return self.client.post("/logout", headers=headers)

    def test_initial_users(self):
        """Test initial users."""
        with app.app_context():
            users = User.query.all()

            # We should have only 1 user ("admin")
            assert len(users) == 1
            u = users[0]
            assert u.username == self.admin_username
            assert u.enabled
            assert u.admin

    def test_admin_login(self):
        """Test administrator user login and logout."""
        # Login
        r = self._login(self.admin_username, self.admin_password)

        self.assertEqual(r.status_code, 200)
        self.assertEqual("message" in r.json, True)
        self.assertEqual("result" in r.json, True)
        self.assertEqual("access_token" in r.json["result"], True)

        access_token = r.json["result"]["access_token"]
        self.assertEqual(access_token != "", True)

        # Logout
        r = self._logout(access_token)
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
