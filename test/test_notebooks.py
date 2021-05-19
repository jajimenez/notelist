"""Notebook resources unit tests."""

import unittest
import common


class NotebookListTestCase(common.BaseTestCase):
    """Notebook List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Notebook List resource.

        This test logs in as some user, creates some notebooks and then tries
        to get the user's notebook list, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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
        notebook_id = r.json["result"]

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
        # Get list without providing the access token
        r = self.client.get("/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook List resource.

        This test tries to get the user's notebook list providing an invalid
        access token, which shouldn't work.
        """
        # Get list providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/notebooks", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post(self):
        """Test the Post method of the Notebook List resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/notebooks")

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
        r = self.client.delete("/notebooks")

        # Check status code
        self.assertEqual(r.status_code, 405)


class NotebookTestCase(common.BaseTestCase):
    """Notebook resource unit tests."""

    def test_get(self):
        """Test the Get method of the Notebook resource.

        This test logs in as some user, creates a notebook and then tries to
        get this notebook, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Get the data of the notebook
        r = self.client.get(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        notebook = r.json["result"]
        self.assertEqual(type(notebook), dict)

        # Check notebook
        self.assertEqual(len(notebook), 2)
        self.assertIn("id", notebook)
        self.assertIn("name", notebook)
        self.assertEqual(notebook["id"], notebook_id)
        self.assertEqual(notebook["name"], n["name"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Notebook resource.

        This test tries to get a notebook without providing the access token,
        which shouldn't work.
        """
        # Get the notebook with ID 1 (which doesn't exist) without providing
        # the access token.
        r = self.client.get("/notebook/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Notebook resource.

        This test tries to get a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Get the notebook with ID 1 (which doesn't exist) providing an invalid
        # access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the Notebook resource.

        This test tries to get a notebook of some user as another user, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_notebook_not_found(self):
        """Test the Get method of the Notebook resource.

        This test tries to get a notebook that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a notebook, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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

        This test tries to create a notebook without providing the access
        token, which shouldn't work.
        """
        # Create notebook
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Create a notebook providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_missing_fields(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a notebook with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook (without data)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.post("/notebook", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create notebook (with empty data)
        r = self.client.post("/notebook", headers=headers, json=dict())

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_user(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a new notebook specifying its user, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"user_id": 1, "name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_invalid_fields(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a notebook providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook", "invalid_field": "1234"}
        r = self.client.post("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_notebook_exists(self):
        """Test the Post method of the Notebook resource.

        This test tries to create a notebook with the same name of an existing
        notebook of the request user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
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

        This test tries to create a notebook, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

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

        This test tries to edit one of the request user's notebooks, which
        should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Edit the notebook
        new_notebook = {"name": "Test Notebook 2"}
        r = self.client.put(
            f"/notebook/{notebook_id}", headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get notebook data
        r = self.client.get(f"/notebook/{notebook_id}", headers=headers)
        notebook = r.json["result"]

        # Check data
        self.assertEqual(len(notebook), 2)
        self.assertIn("id", notebook)
        self.assertIn("name", notebook)
        self.assertEqual(notebook["id"], notebook_id)
        self.assertEqual(notebook["name"], new_notebook["name"])

    def test_put_new_missing_access_token(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a new notebook without providing the access
        token, which shouldn't work.
        """
        # Create a notebook without providing the access token
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_edit_new_missing_access_token(self):
        """Test the Put method of the Notebook resource.

        This test tries to edit a notebook without providing the access token,
        which shouldn't work.
        """
        # Edit the user with ID 1 (whose username is "self.admin["username"]")
        # without providing the access token.
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook/1", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_new_invalid_access_token(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Create a notebook providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the Notebook resource.

        This test tries to edit a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Edit the user with ID 1 (whose username is "self.admin["username"]")
        # providing an invalid access token ("1234").
        headers = {"Authorization": "Bearer 1234"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook/1", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_edit_unauthorized_user(self):
        """Test the Get method of the Notebook resource.

        This test creates a notebook of some user, and then tries to edit the
        notebook as another user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit the notebook as the administrator user
        headers = {"Authorization": f"Bearer {access_token}"}
        new_notebook = {"name": "Test Notebook 2"}

        r = self.client.put(
            f"/notebook/{notebook_id}", headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_missing_fields(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a notebook with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook (without data)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.put("/notebook", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create notebook (with empty data)
        r = self.client.put("/notebook", headers=headers, json=dict())

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_user(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a notebook specifying its user, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"user_id": self.reg1["id"], "name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_invalid_fields(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a notebook providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a notebook providing an invalid field ("invalid_field")
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook", "invalid_field": "1234"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_user(self):
        """Test the Put method of the Notebook resource.

        This test tries to change the user of some notebook, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Change notebook user
        new_notebook = {"id": notebook_id, "user_id": self.reg2["id"]}
        r = self.client.put("/notebook", headers=headers, json=new_notebook)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_invalid_fields(self):
        """Test the Put method of the Notebook resource.

        This test tries to edit a notebook providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Edit the notebook providing an invalid field ("invalid_field")
        n = {"name": "Test Notebook", "invalid_field": "1234"}
        r = self.client.put(
            f"/notebook/{notebook_id}", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_notebook_exists(self):
        """Test the Put method of the Notebook resource.

        This test tries to create a notebook with the same name of an existing
        notebook of the request user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create same notebook again
        r = self.client.put("/notebook", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_notebook_not_found(self):
        """Test the Put method of the Notebook resource.

        This test tries to edit a notebook that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit a notebook with ID 1 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook/1", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete(self):
        """Test the Delete method of the Notebook resource.

        This test creates a notebook and then tries to delete it, which should
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Get user notebook list
        r = self.client.get("/notebooks", headers=headers)
        notebooks = r.json["result"]

        # Check list
        self.assertEqual(len(notebooks), 1)
        self.assertEqual(notebooks[0]["name"], n["name"])

        # Delete notebook
        r = self.client.delete(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get user notebook list
        r = self.client.get("/notebooks", headers=headers)
        notebooks = r.json["result"]

        # Check list
        self.assertEqual(len(notebooks), 0)

    def test_delete_missing_access_token(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete an existing notebook without providing the
        access token, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Delete notebook without providing the access token
        r = self.client.delete(f"/notebook/{notebook_id}")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Delete notebook providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.delete(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_delete_access_token_not_fresh(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook providing a not fresh access
        token, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]
        refresh_token = r.json["result"]["refresh_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Get a new, not fresh, access token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        r = self.client.get("/refresh", headers=headers)
        access_token = r.json["result"]["access_token"]

        # Delete notebook providing a not fresh access token
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/user/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_unauthorized_user(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook of a user different than the
        request user, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/notebook/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete_notebook_not_found(self):
        """Test the Delete method of the Notebook resource.

        This test tries to delete a notebook that doesn't exist, which
        shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete the notebook with ID 1 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete("/notebook/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":
    unittest.main()
