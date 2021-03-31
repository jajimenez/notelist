"""User resources unit tests."""

import unittest
import common


class LoginTestCase(common.BaseTestCase):
    """Login resource unit tests."""

    def test_post_ok(self):
        """Test the Get method of the Login resource.

        This test tries to log in as an existing user with valid credentials,
        which should work.
        """
        # Log in as the "admin" user
        data = {
            "username": self.admin_username, "password": self.admin_password}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertEqual(type(result), dict)

        # Check access token
        self.assertIn("access_token", result)
        access_token = result["access_token"]
        self.assertEqual(type(access_token), str)
        self.assertNotEqual(access_token, "")

        # Check refresh token
        self.assertIn("refresh_token", result)
        refresh_token = result["refresh_token"]
        self.assertEqual(type(refresh_token), str)
        self.assertNotEqual(refresh_token, "")

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

    def test_post_missing_username(self):
        """Test the Get method of the Login resource.

        This test tries to log in as an existing user without providing its
        username, which shouldn't work.
        """
        # Log in as the "admin" user
        data = {"password": self.admin_password}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_missing_password(self):
        """Test the Get method of the Login resource.

        This test tries to log in as an existing user without providing its
        password, which shouldn't work.
        """
        # Log in as the "admin" user
        data = {"username": self.admin_username}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_wrong_password(self):
        """Test the Get method of the Login resource.

        This test tries to log in as an existing user providing a wrong
        password, which shouldn't work.
        """
        # Log in as the "admin" user
        data = {
            "username": self.admin_username,
            "password": self.admin_password + "_"}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
