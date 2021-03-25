"""User unit tests."""

import unittest
from typing import Dict
from flask.wrappers import Response

import common


class UserTestCase(common.BaseTestCase):
    """User unit tests."""

    def _login(self, username: str, password: str) -> Response:
        """Log in given a username and a password.

        :param username: Username.
        :param password: User password.
        :return: Response.
        """
        data = {"username": username, "password": password}
        return self.client.post("/login", json=data)

    def _get_headers(self, access_token: str) -> Dict:
        """Return the request headers with the access token.

        :param access_token: Access token.
        :return: Dictionary containing the request headers.
        """
        return {"Authorization": f"Bearer {access_token}"}

    def _logout(self, access_token: str) -> Response:
        """Log out given an access token.

        :param access_token: Access token.
        :return: Response.
        """
        headers = self._get_headers(access_token)
        return self.client.post("/logout", headers=headers)

    def _get_users(self) -> Response:
        """Get the list of users.

        :return: Response.
        """
        # Login as "admin"
        r = self._login(self.admin_username, self.admin_password)
        access_token = r.json["result"]["access_token"]

        # Make API request
        headers = self._get_headers(access_token)
        return self.client.get("/users", headers=headers)

    def _create_user(self, username: str, password: str) -> Response:
        """Create a new user.

        :param username: Username.
        :param password: Password.
        :return: Response.
        """
        # Login as "admin"
        r = self._login(self.admin_username, self.admin_password)
        access_token = r.json["result"]["access_token"]

        # Make API request
        headers = self._get_headers(access_token)
        data = {
            "username": username,
            "password": password,
            "admin": False,
            "enabled": True}

        return self.client.post("/user", headers=headers, json=data)

    def test_admin_login(self):
        """Test the "admin" user login and logout."""
        # Invalid login
        r = self._login(self.admin_username, self.admin_password + "_")
        self.assertEqual(r.status_code, 401)

        # Valid login
        r = self._login(self.admin_username, self.admin_password)

        self.assertEqual(r.status_code, 200)
        self.assertIn("result", r.json)

        result = r.json["result"]
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        self.assertIn("user_id", result)

        access_token = result["access_token"]
        self.assertNotEqual(access_token, "")

        # Invalid logout
        r = self._logout(access_token + "_")
        self.assertEqual(r.status_code, 422)

        # Logout
        r = self._logout(access_token)
        self.assertEqual(r.status_code, 200)

    def test_initial_users(self):
        """Test the initial users."""
        r = self._get_users()
        self.assertEqual(r.status_code, 200)
        self.assertIn("result", r.json)

        result = r.json["result"]
        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)

        u = result[0]
        self.assertEqual(u["username"], self.admin_username)
        self.assertTrue(u["enabled"])
        self.assertTrue(u["admin"])

    def test_new_user(self):
        """Test the creation of a new user."""
        # Create the user
        username = "test"
        password = "test_password"

        r = self._create_user(username, password)
        self.assertEqual(r.status_code, 201)

        # User list
        r = self._get_users()
        self.assertIn("result", r.json)

        result = r.json["result"]
        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 2)

        u = result[1]

        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, u)

        self.assertNotIn("password", u)
        self.assertEqual(u["username"], username)
        self.assertTrue(u["enabled"])
        self.assertFalse(u["admin"])

        # Invalid login
        r = self._login(username, password + "_")
        self.assertEqual(r.status_code, 401)

        # Valid login
        r = self._login(username, password)
        self.assertEqual(r.status_code, 200)
        self.assertIn("result", r.json)

        result = r.json["result"]
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        self.assertIn("user_id", result)

        access_token = result["access_token"]
        user_id = result["user_id"]

        # Check that the user can get their own data
        headers = self._get_headers(access_token)
        r = self.client.get(f"/user/{user_id}", headers=headers)

        self.assertEqual(r.status_code, 200)
        self.assertIn("result", r.json)

        # Check the user data
        u = r.json["result"]
        self.assertEqual(type(u), dict)

        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, u)

        self.assertNotIn("password", u)
        self.assertEqual(u["username"], username)
        self.assertTrue(u["enabled"])
        self.assertFalse(u["admin"])

        # Invalid logout
        r = self._logout(access_token + "_")
        self.assertEqual(r.status_code, 422)

        # Valid logout
        r = self._logout(access_token)
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
