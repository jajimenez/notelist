"""Notebook resources unit tests."""

import unittest
import common


class NotebookListTestCase(common.BaseTestCase):
    """Notebook List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Notebook List resource.

        This test logs in as some user, creates some notebooks and then tries
        to get their list of notebooks, which should work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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
        r = self.client.get("/notebooks", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebooks = r.json["result"]
        self.assertEqual(type(notebooks), list)

        # Check list
        self.assertEqual(len(notebooks), 0)

        # Create notebook
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

        # Get list
        r = self.client.get("/notebooks", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebooks = r.json["result"]
        self.assertEqual(type(notebooks), list)

        # Check list
        self.assertEqual(len(notebooks), 1)
        notebook = notebooks[0]
        self.assertEqual(notebook["id"], notebook_id)
        self.assertEqual(notebook["name"], n["name"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Notebook List resource.

        This test tries to get the list of notebooks of the request user
        without providing the access token, which shouldn't work.
        """
        # Get list
        r = self.client.get(f"/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook List resource.

        This test logs in as some user and then tries to get their list of
        notebooks given an invalid access token, which shouldn't work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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
        r = self.client.get(f"/notebooks", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post(self):
        """Test the Post method of the Notebook List resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.put("/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_put(self):
        """Test the Put method of the Notebook List resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Notebook List resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.put("/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 405)


class NotebookTestCase(common.BaseTestCase):
    """Notebook resource unit tests."""

    def test_get(self):
        """Test the Get method of the Notebook resource.

        This test logs in as some user, creates a notebook and then tries to
        get this notebook, which should work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

        # Get the data of the notebook
        r = self.client.get(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebook = r.json["result"]
        self.assertEqual(type(notebook), dict)

        # Check notebook
        self.assertEqual(notebook["id"], notebook_id)
        self.assertEqual(notebook["name"], n["name"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Notebook resource.

        This test tries to get a notebook without providing the access token,
        which shouldn't work.
        """
        # Get notebook
        r = self.client.get(f"/notebook/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook resource.

        This test logs in as some user and then tries to get a notebook given
        an invalid access token, which shouldn't work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Get notebook providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.get(f"/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the Notebook resource.

        This test logs in as an administrator user, creates a new user, creates
        a notebook of the new user, and then tries to get the notebook as the
        administrator user, which shouldn't work (even for administrator
        users).
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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
        headers1 = {"Authorization": f"Bearer {access_token}"}
        u = {"username": "test", "password": "test_password", "enabled": True}
        r = self.client.post("/user", headers=headers1, json=u)

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

        # Create a notebook of the new user
        headers2 = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers2, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

        # Get the notebook as the "root" user
        r = self.client.get(f"/notebook/{notebook_id}", headers=headers1)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_notebook_not_found(self):
        """Test the Get method of the Notebook resource.

        This test logs in as some user and then tries to get a notebook that
        doesn't exist for this user, which shouldn't work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Get a notebook that doesn't exist
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post(self):
        """Test the Post method of the Notebook resource.

        This test logs in as some user and then tries to create a new notebook,
        which should work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

    def test_post_missing_access_token(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a new notebook without providing the access
        token, which shouldn't work.
        """
        # Create a notebook
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Notebook resource.

        This test logs in as some user and then tries to create a new notebook
        providing an invalid access token, which shouldn't work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_missing_fields(self):
        """Test the Post method of the Notebook resource.

        This test logs in as some user and then tries to create a new notebook
        with some mandatory field missing, which shouldn't work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Create a notebook without its name.
        headers = {"Authorization": f"Bearer {access_token}"}
        n = dict()  # Empty dictionary
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_notebook_exists(self):
        """Test the Post method of the Notebook resource.

        This test logs in as some user and then tries to create a new notebook
        with the same name of an existing notebook of this user, which
        shouldn't work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create the same notebook again
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new(self):
        """Test the Put method of the Notebook resource.

        This test logs in as some user and then tries to create a new notebook,
        which should work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

    def test_put_edit(self):
        """Test the Put method of the Notebook resource.

        This test logs in as some user and then tries to edit one of their
        notebooks, which should work.
        """
        # Log in as the "root" user
        data = {"username": "root", "password": self.root_password}
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

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

        # Edit the notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        new_notebook = {
            "id": notebook_id,
            "name": "Test Notebook 2"}
        r = self.client.put(f"/notebook", headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get notebook data
        r = self.client.get(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebook = r.json["result"]
        self.assertEqual(type(notebook), dict)

        # Check data
        self.assertEqual(notebook["id"], notebook_id)
        self.assertEqual(notebook["name"], new_notebook["name"])


if __name__ == "__main__":
    unittest.main()
