"""User resources unit tests."""

import unittest
import common


class LoginTestCase(common.BaseTestCase):
    """Login resource unit tests."""

    def test_post(self):
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

    def test_post_invalid_password(self):
        """Test the Get method of the Login resource.

        This test tries to log in as an existing user providing an invalid
        password, which shouldn't work.
        """
        # Log in as the "admin" user
        data = {
            "username": self.admin_username,
            "password": self.admin_password + "_"}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get(self):
        """Test the Get method of the Login resource.

        This test tries to call the Get method, which shouldn't work.
        """
        r = self.client.get("/login")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_put(self):
        """Test the Put method of the Login resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/login")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Login resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/login")

        # Check status code
        self.assertEqual(r.status_code, 405)


class TokenRefreshTestCase(common.BaseTestCase):
    """Token Refresh resource unit tests."""

    def test_post(self):
        """Test the Post method of the Token Refresh resource.

        This test tries to log in as an existing user and get a new, not fresh,
        access token given the user refresh token, which should work.
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

        # Check refresh token
        self.assertIn("refresh_token", result)
        refresh_token = result["refresh_token"]
        self.assertEqual(type(refresh_token), str)
        self.assertNotEqual(refresh_token, "")

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.post("/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertEqual(type(result), dict)

        # Check new access token
        self.assertIn("access_token", result)
        access_token = result["access_token"]
        self.assertEqual(type(access_token), str)
        self.assertNotEqual(access_token, "")

    def test_post_missing_refresh_token(self):
        """Test the Post method of the Token Refresh resource.

        This test tries to get a new, not fresh, access token without providing
        a refresh token, which shouldn't work.
        """
        # Get access token
        r = self.client.post("/refresh")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_refresh_token(self):
        """Test the Post method of the Token Refresh resource.

        This test tries to log in as an existing user and get a new, not fresh,
        access token given an invalid refresh token, which shouldn't work.
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

        # Get a new, not fresh, access token providing the access token instead
        # of the refresh token.
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.post("/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get(self):
        """Test the Get method of the Token Refresh resource.

        This test tries to call the Get method, which shouldn't work.
        """
        r = self.client.get("/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_put(self):
        """Test the Put method of the Token Refresh resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Token Refresh resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)


class LogoutTestCase(common.BaseTestCase):
    """Logout resource unit tests."""

    def test_post(self):
        """Test the Get method of the Logout resource.

        This test tries to log in as an existing user with valid credentials
        and then log out, which should work.
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

        # Log out
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.post("/logout", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_post_missing_access_token(self):
        """Test the Post method of the Logout resource.

        This test tries to log out without providing an access token, which
        shouldn't work.
        """
        # Logout
        r = self.client.post("/logout")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Logout resource.

        This test tries to log out given an invalid access token, which
        shouldn't work.
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

        # Log out providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.post("/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
