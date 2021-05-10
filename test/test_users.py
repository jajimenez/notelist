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

        This test tries to log in as some user with valid credentials, which
        should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
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
        self.assertEqual(user_id, self.reg1["id"])

    def test_post_missing_fields(self):
        """Test the Get method of the Login resource.

        This test tries to log in as some user with some mandatory field
        missing, which shouldn't work.
        """
        # Log in (without data)
        r = self.client.post("/login")

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Log in (without username)
        data = {"password": self.reg1["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Log in (without password)
        data = {"username": self.reg1["username"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_disabled_user(self):
        """Test the Get method of the Login resource.

        This test tries to log in as some disabled user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg2["username"],
            "password": self.reg2["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_user_not_found(self):
        """Test the Get method of the Login resource.

        This test tries to log in as a user that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {"username": "test", "password": "test_password"}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_password(self):
        """Test the Get method of the Login resource.

        This test tries to log in as some user providing an invalid password,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"] + "_"}
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

        This test tries to get a new, not fresh, access token providing the
        user refresh token, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        refresh_token = r.json["result"]["refresh_token"]

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.get("/refresh", headers=headers)

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

    def test_get_missing_refresh_token(self):
        """Test the Get method of the Token Refresh resource.

        This test tries to get a new, not fresh, access token without providing
        a refresh token, which shouldn't work.
        """
        # Get access token
        r = self.client.get("/refresh")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_refresh_token(self):
        """Test the Get method of the Token Refresh resource.

        This test tries to get a new, not fresh, access token given an invalid
        refresh token, which shouldn't work.
        """
        # Get a new, not fresh, access token providing an invalid access token
        # ("1234").
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post(self):
        """Test the Post method of the Token Refresh resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/refresh")

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

    def test_get(self):
        """Test the Get method of the Logout resource.

        This test logs in as some user with valid credentials and then tries to
        log out, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Log out
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/logout", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_get_missing_access_token(self):
        """Test the Get method of the Logout resource.

        This test tries to log out without providing an access token, which
        shouldn't work.
        """
        # Log out without providing the access token
        r = self.client.get("/logout")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Logout resource.

        This test tries to log out providing an invalid access token, which
        shouldn't work.
        """
        # Log out providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/refresh", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post(self):
        """Test the Post method of the Logout resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/logout")

        # Check status code
        self.assertEqual(r.status_code, 405)

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
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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
        self.assertEqual(len(users), 3)

        for u in users:
            self.assertEqual(type(u), dict)

            for i in ("id", "username", "admin", "enabled", "name", "email"):
                self.assertIn(i, u)

            self.assertNotIn("password", u)

        for i, u in enumerate((self.admin, self.reg1, self.reg2)):
            self.assertEqual(users[i]["id"], u["id"])
            self.assertEqual(users[i]["username"], u["username"])

    def test_get_missing_access_token(self):
        """Test the Post method of the User List resource.

        This test tries to get the list of users without providing an access
        token, which shouldn't work.
        """
        # Get list without providing the access token
        r = self.client.get("/users")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Post method of the User List resource.

        This test tries to get the list of users providing an invalid access
        token, which shouldn't work.
        """
        # Get list providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/users", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Post method of the User List resource.

        This test logs in as a not administrator user and then tries to get the
        list of users, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get user data
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f'/user/{self.admin["id"]}', headers=headers)

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
        self.assertEqual(user["id"], self.admin["id"])
        self.assertEqual(user["username"], self.admin["username"])
        self.assertTrue(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], self.admin["name"])
        self.assertIsNone(user["email"])

        # Get another user's data
        r = self.client.get(f'/user/{self.reg1["id"]}', headers=headers)

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
        self.assertEqual(user["id"], self.reg1["id"])
        self.assertEqual(user["username"], self.reg1["username"])
        self.assertFalse(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], self.reg1["name"])
        self.assertIsNone(user["email"])

    def test_get_not_admin(self):
        """Test the Get method of the User resource.

        This test logs in as a not administrator user and then tries to get its
        data, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get user data
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f'/user/{self.reg1["id"]}', headers=headers)

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
        self.assertEqual(user["id"], self.reg1["id"])
        self.assertEqual(user["username"], self.reg1["username"])
        self.assertFalse(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], self.reg1["name"])
        self.assertIsNone(user["email"])

    def test_get_missing_access_token(self):
        """Test the Get method of the User resource.

        This test tries to get the data of a user without providing the access
        token, which shouldn't work.
        """
        # Get the data of the user with ID 1 (which doesn't exist)
        r = self.client.get("/user/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the User resource.

        This test tries to get the data of some user providing an invalid
        access token, which shouldn't work.
        """
        # Get the user providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get(f'/user/{self.reg1["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the User resource.

        This test logs in as a not administrator user and then tries to get the
        data of another user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get another user's data
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f'/user/{self.reg2["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_user_not_found(self):
        """Test the Get method of the User resource.

        This test logs in as an administrator user and then tries to get the
        data of some user that doesn't exist, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get the data of the user with ID 4 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/user/4", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)

    def test_post(self):
        """Test the Post method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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
        user = r.json["result"]

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
        # Create a user without providing the access token
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the User resource.

        This test tries to create a new user providing an invalid access token,
        which shouldn't work.
        """
        # Create a user providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_unauthorized_user(self):
        """Test the Post method of the User resource.

        This test logs in as a not administrator user and then tries to create
        a new user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post_missing_fields(self):
        """Test the Post method of the User resource.

        This test tries to create new users with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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

        This test tries to create a new user with a password that has less than
        8 characters and another user with a password that has more than 100
        characters, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create users
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            u = {"username": "test", "password": p}
            r = self.client.post("/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

    def test_post_invalid_fields(self):
        """Test the Post method of the User resource.

        This test tries to create a new user providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password", "invalid_field": "1234"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_user_exists(self):
        """Test the Post method of the User resource.

        This test tries to create a new user with the same username of another
        user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": self.reg1["username"], "password": "test_password"}
        r = self.client.post("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new(self):
        """Test the Put method of the User resource.

        This test logs in as an administrator user and then tries to create a
        new user, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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
        itself and another user, which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the user fields except the username (which is not allowed to be
        # modified).
        headers = {"Authorization": f"Bearer {access_token}"}
        new_user = {
            "password": "test_password",
            "admin": True,
            "enabled": True,
            "name": "Admin 2",
            "email": None}

        r = self.client.put(
            f'/user/{self.admin["id"]}', headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user data
        r = self.client.get(f'/user/{self.admin["id"]}', headers=headers)
        user = r.json["result"]

        # Check data
        self.assertEqual(len(user), 6)

        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

            if i not in ("id", "username"):
                self.assertEqual(user[i], new_user[i])

        self.assertNotIn("password", user)
        self.assertEqual(user["id"], self.admin["id"])
        self.assertEqual(user["username"], self.admin["username"])

        # Edit another user
        new_user = {
            "username": "test_2",
            "password": "test_password_2",
            "admin": True,
            "enabled": True,
            "name": "Test 2",
            "email": None}

        r = self.client.put(
            f'/user/{self.reg1["id"]}', headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user data
        r = self.client.get(f'/user/{self.reg1["id"]}', headers=headers)
        user = r.json["result"]

        # Check data
        self.assertEqual(len(user), 6)

        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

            if i != "id":
                self.assertEqual(user[i], new_user[i])

        self.assertNotIn("password", user)
        self.assertEqual(user["id"], self.reg1["id"])

    def test_put_edit_not_admin(self):
        """Test the Put method of the User resource.

        This test logs in as a not administrator user and then tries to edit
        itself, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user
        headers = {"Authorization": f"Bearer {access_token}"}
        new_user = {
            "password": "test_password_2",
            "name": "Test 2",
            "email": None}

        r = self.client.put(
            f'/user/{self.reg1["id"]}', headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user data
        r = self.client.get(f'/user/{self.reg1["id"]}', headers=headers)
        user = r.json["result"]

        # Check data
        self.assertEqual(len(user), 6)

        for i in ("id", "username", "admin", "enabled", "name", "email"):
            self.assertIn(i, user)

        self.assertNotIn("password", user)
        self.assertEqual(user["id"], self.reg1["id"])
        self.assertEqual(user["username"], self.reg1["username"])
        self.assertFalse(user["admin"])
        self.assertTrue(user["enabled"])
        self.assertEqual(user["name"], new_user["name"])
        self.assertEqual(user["email"], new_user["email"])

        # Log in with the old password
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 401)

        # Log in with the new password
        data = {
            "username": self.reg1["username"],
            "password": new_user["password"]}
        r = self.client.post("/login", json=data)

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_put_new_missing_access_token(self):
        """Test the Put method of the User resource.

        This test tries to create a new user without providing the access
        token, which shouldn't work.
        """
        # Create a user without providing the access token
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/user", json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_edit_missing_access_token(self):
        """Test the Put method of the User resource.

        This test tries to edit a user without providing the access token,
        which shouldn't work.
        """
        # Edit user without providing the access token
        u = {"name": "Test User"}
        r = self.client.put(f'/user/{self.reg1["id"]}', json=u)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_new_invalid_access_token(self):
        """Test the Put method of the User resource.

        This test tries to create a new user providing an invalid access token,
        which shouldn't work.
        """
        # Create a user providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        u = {"username": "test", "password": "test_password"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the User resource.

        This test tries to edit a user providing an invalid access token, which
        shouldn't work.
        """
        # Edit user providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        u = {"username": "test", "password": "test_password"}

        r = self.client.put(
            f'/user/{self.reg1["id"]}', headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_new_unauthorized_user(self):
        """Test the Put method of the User resource.

        This test logs in as a not administrator user and then tries to create
        a new user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a new, not administrator, user.
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {
            "username": "test",
            "password": "test_password",
            "admin": False,
            "enabled": True}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_edit_unauthorized_user(self):
        """Test the Put method of the User resource.

        This test logs in as a not administrator user, tries to edit some
        fields of itself which are not allowed to be modified and then tries to
        modify another user, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the "username", "admin" and "enabled" fields of the new user
        headers = {"Authorization": f"Bearer {access_token}"}
        user = {
            "username": "test",
            "admin": False,
            "enabled": True}

        for i in ("username", "admin", "enabled"):
            # Edit the field
            new_user = {i: user[i]}

            r = self.client.put(
                f'/user/{self.reg1["id"]}', headers=headers, json=new_user)

            # Check status code
            self.assertEqual(r.status_code, 403)

        # Edit another user
        new_user = {"name": "Test User"}
        r = self.client.put(
            f'/user/{self.reg2["id"]}', headers=headers, json=new_user)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_new_missing_fields(self):
        """Test the Put method of the User resource.

        This test tries to create new users with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user without its username
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create a user without its password
        u = {"username": "test"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_invalid_fields(self):
        """Test the Put method of the User resource.

        This test tries to create a new user providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a user providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password", "invalid_field": "1234"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_invalid_fields(self):
        """Test the Put method of the User resource.

        This test tries to edit a user providing some invalid/unexpected field,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"], "password":
            self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"password": "test_password", "invalid_field": "1234"}

        r = self.client.put(
            f'/user/{self.reg1["id"]}', headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_password_length(self):
        """Test the Put method of the User resource.

        This test tries to create a new user with a password that has less than
        8 characters and another user with a password that has more than 100
        characters, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create users
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            u = {"username": "test", "password": p}
            r = self.client.put("/user", headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

    def test_put_edit_password_length(self):
        """Test the Put method of the User resource.

        This test logs in as some user, tries to change its password with a new
        one that has less than 8 characters and then tries to change it with
        another one that has more than 100 characters, which shouldn't work in
        either case.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit user
        headers = {"Authorization": f"Bearer {access_token}"}

        for p in ("test", "test" * 100):
            u = {"password": p}
            r = self.client.put(
                f'/user/{self.reg1["id"]}', headers=headers, json=u)

            # Check status code
            self.assertEqual(r.status_code, 400)

    def test_put_new_user_exists(self):
        """Test the Put method of the User resource.

        This test tries to create a new user with the same username of another
        user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create user
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"username": self.reg1["username"], "password": "test_password"}
        r = self.client.put("/user", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_user_not_found(self):
        """Test the Put method of the User resource.

        This tries to edit some user that doesn't exist, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the user with ID 4 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        u = {"name": "Test"}
        r = self.client.put("/user/4", headers=headers, json=u)

        # Check status code
        self.assertEqual(r.status_code, 404)

    def test_delete(self):
        """Test the Delete method of the User resource.

        This test logs in as an administrator user and tries to delete a user,
        which should work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f'/user/{self.reg1["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get the user list
        r = self.client.get("/users", headers=headers)
        users = r.json["result"]

        # Check list
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["id"], self.admin["id"])
        self.assertEqual(users[1]["id"], self.reg2["id"])

    def test_delete_missing_access_token(self):
        """Test the Delete method of the User resource.

        This test tries to delete some user without providing the access token,
        which shouldn't work.
        """
        # Delete user
        r = self.client.delete(f'/user/{self.reg1["id"]}')

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the User resource.

        This test tries to delete some user providing an invalid access token,
        which shouldn't work.
        """
        # Delete user providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.delete(f'/user/{self.reg1["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_delete_access_token_not_fresh(self):
        """Test the Delete method of the User resource.

        This test tries to delete some user providing a not fresh access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        refresh_token = r.json["result"]["refresh_token"]

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.get("/refresh", headers=headers)
        access_token = r.json["result"]["access_token"]

        # Delete user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f'/user/{self.reg1["id"]}', headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_unauthorized_user(self):
        """Test the Delete method of the User resource.

        This test logs in as a not administrator user and then tries to delete
        itself and another user, which shouldn't work in either case.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete users
        headers = {"Authorization": f"Bearer {access_token}"}

        for i in (self.reg1["id"], self.reg2["id"]):
            r = self.client.delete(f"/user/{i}", headers=headers)

            # Check status code
            self.assertEqual(r.status_code, 403)

    def test_delete_user_not_found(self):
        """Test the Delete method of the User resource.

        This test tries to delete a user that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete the user with ID 4 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete("/user/4", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
