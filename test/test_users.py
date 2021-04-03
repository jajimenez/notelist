"""User resources unit tests."""

import unittest
import common


class LoginTestCase(common.BaseTestCase):
    """Login resource unit tests."""

    def test_get(self):
        """Test the Get method of the Login resource.

        This test tries to call the Get method, which shouldn't work.
        """
        r = self.client.get("/login")

        # Check status code
        self.assertEqual(r.status_code, 405)

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

    def test_post_missing_fields(self):
        """Test the Get method of the Login resource.

        This test tries to log in as an existing user with some mandatory field
        missing, which shouldn't work.
        """
        # Log in as the "admin" user without providing its username
        data = {"password": self.admin_password}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Log in as the "admin" user without providing its password
        data = {"username": self.admin_username}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_disabled_user(self):
        """Test the Get method of the Login resource.

        This test tries to log in as a disabled user, which shouldn't work.
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

        # Create a disabled user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password", "enabled": False}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Login as the new user
        data = {"username": u["username"], "password": u["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_user_not_found(self):
        """Test the Get method of the Login resource.

        This test tries to log in as a user that doesn't exist, which shouldn't
        work.
        """
        # Log in as the "admin" user
        data = {"username": "test", "password": "test_password"}
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

    def test_get(self):
        """Test the Get method of the Token Refresh resource.

        This test tries to call the Get method, which shouldn't work.
        """
        r = self.client.get("/refresh")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_post(self):
        """Test the Post method of the Token Refresh resource.

        This test logs in as an existing user and tries to get a new,
        not fresh, access token given the user refresh token, which should
        work.
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

        This test logs in as an existing user and tries to get a new, not
        fresh, access token given an invalid refresh token, which shouldn't
        work.
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

    def test_get(self):
        """Test the Get method of the Logout resource.

        This test tries to call the Get method, which shouldn't work.
        """
        r = self.client.get("/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_post(self):
        """Test the Post method of the Logout resource.

        This test logs in as an existing user with valid credentials and then
        tries to log out, which should work.
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

        This test logs in as an existing user and then tries to log out given
        an invalid access token, which shouldn't work.
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

    def test_put(self):
        """Test the Put method of the Logout resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Logout resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)


class UserListTestCase(common.BaseTestCase):
    """User List resource unit tests."""

    def test_get(self):
        """Test the Get method of the User List resource.

        This test logs in as an administrator user and then tries to get the
        list of users, which should work.
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

        # Get list
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        users = r.json["result"]
        self.assertEqual(type(users), list)

        # Check list
        self.assertEqual(len(users), 1)
        u = users[0]
        self.assertEqual(type(u), dict)

        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, u)

        self.assertNotIn("password", u)
        self.assertEqual(u["username"], self.admin_username)

    def test_post_missing_access_token(self):
        """Test the Post method of the User List resource.

        This test tries to get the list of users without providing an access
        token, which shouldn't work.
        """
        # Get list
        r = self.client.get("/users")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the User List resource.

        This test tries to get the list of users given an invalid access token,
        which shouldn't work.
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

        # Get list providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.get("/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_unauthorized_user(self):
        """Test the Post method of the User List resource.

        This test logs in as a not administrator user and then tries to get the
        list of users, which shouldn't work.
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

        # Create a not administrator user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password", "enabled": True}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Log in as the new user
        data = {"username": u["username"], "password": u["password"]}
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

        # Get list
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put(self):
        """Test the Put method of the User List resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/users")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the User List resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/users")

        # Check status code
        self.assertEqual(r.status_code, 405)


class UserTestCase(common.BaseTestCase):
    """User resource unit tests."""

    def test_get_admin(self):
        """Test the Get method of the User resource.

        This test logs in as an administrator user and then tries to get its
        data and the data of another existing user, which should work in both
        cases.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Get the data of the "admin" user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check user
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

        self.assertNotIn("password", user)
        self.assertEqual(user["id"], user_id)
        self.assertEqual(user["username"], self.admin_username)

        # Create a not administrator user
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Get the data of the new user
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check user
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

        self.assertNotIn("password", user)
        self.assertEqual(user["username"], u["username"])
        self.assertEqual(user["admin"], False)
        self.assertEqual(user["enabled"], False)
        self.assertIsNone(user["name"])
        self.assertIsNone(user["email"])

    def test_get_not_admin(self):
        """Test the Get method of the User resource.

        This test logs in as a not administrator user and then tries to get its
        data, which should work.
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

        # Create a not administrator user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password", "enabled": True}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Login as the new user
        data = {"username": u["username"], "password": u["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertEqual(type(result), dict)

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Get the data of the new user
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check user
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

        self.assertNotIn("password", user)
        self.assertEqual(user["username"], u["username"])
        self.assertEqual(user["admin"], False)
        self.assertEqual(user["enabled"], True)
        self.assertIsNone(user["name"])
        self.assertIsNone(user["email"])

    def test_get_missing_access_token(self):
        """Test the Get method of the User resource.

        This test tries to get the data of a user without providing the access
        token, which shouldn't work.
        """
        # Get data
        r = self.client.get(f"/user/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the User resource.

        This test logs in as an administrator user and then tries to get the
        data of another existing user given an invalid access token, which
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Get data providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the User resource.

        This test logs in as a not administrator user and then tries to get the
        data of another existing user, which shouldn't work.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Create a not administrator user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password", "enabled": True}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Log in as the new user
        data = {"username": u["username"], "password": u["password"]}
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

        # Get the data of the "admin" user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_user_not_found(self):
        """Test the Get method of the User resource.

        This test logs in as an administrator user and then tries to get the
        data of another user that doesn't exist, which shouldn't work.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Get the data of the user "user_id + 1"
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/user/{user_id + 1}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)

    def test_post(self):
        """Test the Post method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user, which should work.
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

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test",
            "email": None}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Get user data
        r = self.client.get(f"/user/{user_id}", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check data
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], u[i])

        self.assertNotIn("password", user)

    def test_post_missing_access_token(self):
        """Test the Post method of the User resource.

        This test tries to create a new user without providing the access
        token, which shouldn't work.
        """
        # Create a user
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user providing an invalid access token, which shouldn't work.
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

        # Create a user providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_unauthorized_user(self):
        """Test the Post method of the User resource.

        This test logs in as a not administrator user and then tries to create
        a new user, which shouldn't work.
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

        # Create a not administrator user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password", "enabled": True}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Login as the new user
        data = {"username": u["username"], "password": u["password"]}
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

        # Create a new user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test_2", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post_missing_fields(self):
        """Test the Post method of the User resource.

        This test logs in as an administrator user and then tries to create new
        users with some mandatory field missing, which shouldn't work.
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

        # Create a user without its username
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create a user without its password
        u = {"username": "test"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_password_length(self):
        """Test the Post method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user with a password that has less than 8 characters and another
        user with a password that has more than 100 characters, which shouldn't
        work in either case.
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

        # Create users
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            u = {"username": "test", "password": p}
            r = self.client.post("/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

    def test_post_user_exists(self):
        """Test the Post method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user with a username that an existing user already has, which
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

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create the same user again
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user, which should work.
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

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test",
            "email": None}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Get user data
        r = self.client.get(f"/user/{user_id}", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check data
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], u[i])

        self.assertNotIn("password", user)

    def test_put_edit_admin(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to edit
        itself and another existing user, which should work.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Edit the "admin" user
        headers = {"Authorization": f"Bearer {access_token}"}
        new_user = {
            "id": user_id,
            "username": "admin_2",
            "password": "test_password",
            "admin": True,
            "enabled": True,
            "name": "Admin 2",
            "email": None}
        r = self.client.put(f"/user", headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user data
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check data
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], new_user[i])

        self.assertNotIn("password", user)

        # Create a new user
        new_user = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test",
            "email": None}
        r = self.client.put("/user", headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Edit the new user
        new_user = {
            "id": user_id,
            "username": "test_2",
            "password": "test_password_2",
            "admin": True,
            "enabled": True,
            "name": "Test 2",
            "email": None}
        r = self.client.put("/user", headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user data
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        user = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check data
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], new_user[i])

        self.assertNotIn("password", user)

    def test_put_edit_not_admin(self):
        """Test the Put method of the User resource.

        This test logs in as a not administrator user and then tries to edit
        itself, which should work.
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

        # Create a new user
        headers = {"Authorization": f"Bearer {access_token}"}
        user = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test",
            "email": None}
        r = self.client.put("/user", headers=headers, json=user)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Log in as the new user
        data = {"username": user["username"], "password": user["password"]}
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

        # Edit the new user
        headers = {"Authorization": f"Bearer {access_token}"}
        new_user = {
            "id": user_id,
            "password": "test_password_2",
            "name": "Test 2",
            "email": None}
        r = self.client.put("/user", headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user data
        r = self.client.get(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        u = r.json["result"]
        self.assertEqual(type(user), dict)

        # Check data
        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, u)

        self.assertNotIn("password", u)
        self.assertEqual(u["id"], user_id)
        self.assertEqual(u["username"], user["username"])
        self.assertFalse(u["admin"])
        self.assertTrue(u["enabled"])
        self.assertEqual(u["name"], new_user["name"])
        self.assertIsNone(u["email"])

        # Log in with the old password
        data = {"username": user["username"], "password": user["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Log in with the new password
        data = {"username": user["username"], "password": new_user["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_put_missing_access_token(self):
        """Test the Put method of the User resource.

        This test tries to create a new user without providing the access
        token, which shouldn't work.
        """
        # Create user
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/user", json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_invalid_access_token(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user providing an invalid access token, which shouldn't work.
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

        # Create a user providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_new_unauthorized_user(self):
        """Test the Put method of the User resource.

        This test logs in as a not administrator user and then tries to create
        a new user, which shouldn't work.
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

        # Create a new, not administrator, user
        headers = {"Authorization": f"Bearer {access_token}"}
        user = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True}
        r = self.client.put("/user", headers=headers, json=user)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Log in as the new user
        data = {"username": user["username"], "password": user["password"]}
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

        # Create a new user
        headers = {"Authorization": f"Bearer {access_token}"}
        user = {"username": "test_2", "password": "test_password_2"}
        r = self.client.put("/user", headers=headers, json=user)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_edit_unauthorized_user(self):
        """Test the Put method of the User resource.

        This test logs in as a not administrator user, tries to edit some
        fields of itself which are not allowed to be modified and then tries to
        modify another existing user, which shouldn't work in either case.
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

        # Check user ID
        self.assertIn("user_id", result)
        admin_user_id = result["user_id"]
        self.assertEqual(type(admin_user_id), int)

        # Create a new, not administrator, user
        headers = {"Authorization": f"Bearer {access_token}"}
        user = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test",
            "email": None}
        r = self.client.put("/user", headers=headers, json=user)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Log in as the new user
        data = {"username": user["username"], "password": user["password"]}
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

        # Edit the "username", "admin" and "enabled" fields of the new user
        headers = {"Authorization": f"Bearer {access_token}"}

        for i in ("username", "admin", "enabled"):
            # Edit the field with the same current value
            new_user = {"id": user_id, i: user[i]}
            r = self.client.put("/user", headers=headers, json=new_user)

            # Check status code
            self.assertEqual(r.status_code, 403)

        # Edit the "admin" user
        new_user = {"id": admin_user_id, "name": "Admin 2"}
        r = self.client.put("/user", headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_missing_fields(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to create new
        users with some mandatory field missing, which shouldn't work.
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

        # Create a user without its username
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create a user without its password
        u = {"username": "test"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_password_length(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user with a password that has less than 8 characters and another
        user with a password that has more than 100 characters, which shouldn't
        work in either case.
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

        # Create users
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            u = {"username": "test", "password": p}
            r = self.client.put("/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

    def test_put_edit_password_length(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user, tries to change its
        password with a new one that has less than 8 characters and then tries
        to change it with another one that has more than 100 characters, which
        shouldn't work in either case.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Edit the "admin" user
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            u = {"id": user_id, "username": "test", "password": p}
            r = self.client.put("/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

    def test_put_new_user_exists(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user with a username that an existing user already has, which
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

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create the same user again
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_user_not_found(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to edit
        another user that doesn't exist, which shouldn't work.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Edit the user with ID "user_id + 1"
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"id": user_id + 1, "name": "Test"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 404)

    def test_delete(self):
        """Test the Delete method of the User resource.

        This test logs in as an administrator user, tries to create a new user
        and then tries to delete it, which should work.
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

        # Create a user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Get the user list
        r = self.client.get("/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        users = r.json["result"]
        self.assertEqual(type(users), list)

        # Check list
        self.assertEqual(len(users), 2)
        self.assertEqual(type(users[0]), dict)
        self.assertEqual(users[0]["username"], data["username"])
        self.assertEqual(type(users[1]), dict)
        self.assertEqual(users[1]["username"], u["username"])

        # Delete user
        r = self.client.delete(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get the user list
        r = self.client.get("/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        users = r.json["result"]
        self.assertEqual(type(users), list)

        # Check list
        self.assertEqual(len(users), 1)
        self.assertEqual(type(users[0]), dict)
        self.assertEqual(users[0]["username"], data["username"])

    def test_delete_missing_access_token(self):
        """Test the Delete method of the User resource.

        This test tries to delete an existing user without providing the access
        token, which shouldn't work.
        """
        # Create a user
        r = self.client.delete("/user/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the User resource.

        This test logs in as an administrator user and then tries to delete
        another existing user providing an invalid access token, which
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Delete the "admin" user providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.delete(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_delete_access_token_not_fresh(self):
        """Test the Delete method of the User resource.

        This test logs in as an administrator user and then tries to delete
        this user providing a not fresh access token, which shouldn't work.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.post(f"/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertEqual(type(result), dict)

        # Check access_token token
        self.assertIn("access_token", result)
        access_token = result["access_token"]
        self.assertEqual(type(access_token), str)
        self.assertNotEqual(access_token, "")

        # Delete the "admin" user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_unauthorized_user(self):
        """Test the Delete method of the User resource.

        This test logs in as a not administrator user and then tries to delete
        itself and another existing user, which shouldn't work in either case.
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

        # Check user ID
        self.assertIn("user_id", result)
        admin_user_id = result["user_id"]
        self.assertEqual(type(admin_user_id), int)

        # Create a new, not administrator, user
        headers = {"Authorization": f"Bearer {access_token}"}
        user = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True,
            "name": "Test",
            "email": None}
        r = self.client.put("/user", headers=headers, json=user)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        user_id = r.json["result"]
        self.assertEqual(type(user_id), int)

        # Log in as the new user
        data = {"username": user["username"], "password": user["password"]}
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

        # Delete the new user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/user/{user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

        # Delete the "admin" user
        r = self.client.delete(f"/user/{admin_user_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete_user_not_found(self):
        """Test the Delete method of the User resource.

        This test logs in as an administrator user and then tries to delete
        another user that doesn't exist, which shouldn't work.
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

        # Check user ID
        self.assertIn("user_id", result)
        user_id = result["user_id"]
        self.assertEqual(type(user_id), int)

        # Delete the user with ID "user_id + 1"
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/user/{user_id + 1}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
