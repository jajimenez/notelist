"""Notebook resources unit tests."""

import unittest
import common


class NotebookListTestCase(common.BaseTestCase):
    """Notebook List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Notebook List resource.

        This test logs in as some user, creates some notebooks and then tries
        to get their notebook list, which should work.
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

        This test tries to get the notebook list of the request user without
        providing the access token, which shouldn't work.
        """
        # Get list
        r = self.client.get(f"/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook List resource.

        This test logs in as some user and then tries to get their notebook
        list providing an invalid access token, which shouldn't work.
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

        This test logs in as some user and then tries to get a notebook
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

        # Get notebook providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.get(f"/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the Notebook resource.

        This test tries to get a notebook of a user from another user, which
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

        # Create a new user
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
        doesn't exist for the user, which shouldn't work.
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

        # Get a notebook that doesn't exist for the user
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

        # Create a notebook providing an invalid access token
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

        # Create a notebook without its name
        headers = {"Authorization": f"Bearer {access_token}"}
        n = dict()  # Empty dictionary
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_notebook_exists(self):
        """Test the Post method of the Notebook resource.

        This test logs in as some user and then tries to create a new notebook
        with the same name of an existing notebook of the user, which shouldn't
        work.
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

    def test_put_missing_access_token(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a new notebook without providing the access
        token, which shouldn't work.
        """
        # Create a notebook
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_invalid_access_token(self):
        """Test the Put method of the Notebook resource.

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

        # Create a notebook providing an invalid access token
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_edit_unauthorized_user(self):
        """Test the Get method of the Notebook resource.

        This test creates a notebook of some user, and then tries to edit the
        notebook as another user, which shouldn't work.
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

        # Create a new user
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

        # Edit the notebook as the "root" user
        new_notebook = {"id": notebook_id, "name": "Test Notebook 2"}
        r = self.client.put(
            f"/notebook", headers=headers1, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_missing_fields(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a new notebook with some mandatory field
        missing, which shouldn't work.
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

        # Create a notebook without providing its name
        headers = {"Authorization": f"Bearer {access_token}"}
        n = dict()  # Empty dictionary
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_notebook_exists(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a new notebook with the same name of an
        existing notebook of the request user, which shouldn't work.
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

        # Create the same notebook again
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_notebook_not_found(self):
        """Test the Put method of the Notebook resource.

        This test tries to edit a notebook that doesn't exist for the request
        user, which shouldn't work.
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

        # Edit a notebook with ID 1 that doesn't exist for the user
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"id": 1, "name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete(self):
        """Test the Delete method of the Notebook resource.

        This test creates a new notebook and then tries to delete it, which
        should work.
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

        # Get the user notebook list
        r = self.client.get("/notebooks", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebooks = r.json["result"]
        self.assertEqual(type(notebooks), list)

        # Check list
        self.assertEqual(len(notebooks), 1)
        self.assertEqual(notebooks[0]["name"], n["name"])

        # Delete the notebook
        r = self.client.delete(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get the user notebook list
        r = self.client.get("/notebooks", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebooks = r.json["result"]
        self.assertEqual(type(notebooks), list)

        # Check list
        self.assertEqual(len(notebooks), 0)

    def test_delete_missing_access_token(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete an existing notebook without providing the
        access token, which shouldn't work.
        """
        # Delete a notebook with ID 1 that doesn't exist
        r = self.client.delete("/notebook/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook providing an invalid access token,
        which shouldn't work.
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

        # Delete a notebook with ID 1 (that doesn't exist for the user)
        # providing an invalid access token.
        headers = {"Authorization": f"Bearer {access_token + '_'}"}
        r = self.client.delete("/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_delete_access_token_not_fresh(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook providing a not fresh access
        token, which shouldn't work.
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

        # Check refresh token
        self.assertIn("refresh_token", result)
        refresh_token = result["refresh_token"]
        self.assertEqual(type(refresh_token), str)
        self.assertNotEqual(refresh_token, "")

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

        # Delete a notebook with ID 1 (that doesn't exist) providing a not
        # fresh access token.
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete("/user/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_unauthorized_user(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook of a user different than the
        request user, which shouldn't work.
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

        # Create a notebook of the "root" user
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        notebook_id = r.json["result"]
        self.assertEqual(type(notebook_id), int)

        # Create a user
        u = {
            "username": "test",
            "password": "test_password",
            "enabled": True}
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

        # Delete the notebook of the "root" user as the new user
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete_notebook_not_found(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook that doesn't exist, which
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

        # Delete the notebook with ID 1, which doesn't exist.
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete("/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":
    unittest.main()
