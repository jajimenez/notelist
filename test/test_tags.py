"""Tag resources unit tests."""

import unittest
import common


class TagListTestCase(common.BaseTestCase):
    """Tag List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Tag List resource.

        This test creates a notebook with some tags and then tries to get the
        notebook's tag list, which should work.
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

        # Create tags
        tags = [
            {"notebook_id": notebook_id, "name": "Test Tag 1"},
            {"notebook_id": notebook_id, "name": "Test Tag 2"}]

        for t in tags:
            r = self.client.post("/tag", headers=headers, json=t)

        # Get notebook tag list
        r = self.client.get(f"/tags/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        res_tags = r.json["result"]
        self.assertEqual(type(res_tags), list)

        # Check list
        c = len(res_tags)
        self.assertEqual(c, 2)

        for i in range(c):
            self.assertEqual(type(res_tags[i]), dict)
            self.assertEqual(res_tags[i]["name"], tags[i]["name"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Tag List resource.

        This test tries to get the tag list of a notebook without providing the
        access token, which shouldn't work.
        """
        # Get the tags of the notebook with ID 1 (which doesn't exist) without
        # providing the access token.
        r = self.client.get("/tags/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Tag List resource.

        This test tries to get the tag list of a notebook providing an invalid
        access token, which shouldn't work.
        """
        # Get the tags of the notebook with ID 1 (which doesn't exist)
        # providing an invalid access token ("1234").
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/tags/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the Tag List resource.

        This test tries to get the tag list of a notebook that doesn't belong
        to the request user, which shouldn't work.
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

        # Get tag list
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/tags/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_missing_notebook_id(self):
        """Test the Get method of the Tag List resource.

        This test tries to get the tag list of a notebook without providing the
        notebook ID, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get tag list
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/tags", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 404)

    def test_post(self):
        """Test the Post method of the Tag List resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r1 = self.client.post("/tags")
        r2 = self.client.post("/tags/1")

        # Check status code
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

    def test_put(self):
        """Test the Put method of the Tag List resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r1 = self.client.put("/tags")
        r2 = self.client.put("/tags/1")

        # Check status code
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Tag List resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r1 = self.client.delete("/tags")
        r2 = self.client.delete("/tags/1")

        # Check status code
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)


class TagTestCase(common.BaseTestCase):
    """Tag resource unit tests."""

    def test_get(self):
        """Test the Get method of the Tag resource.

        This test creates a notebook, adds a tag to the notebook and then tries
        to get the tag, which should work.
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

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#ffffff"}
        r = self.client.post("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Get tag
        r = self.client.get(f"/tag/{tag_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        tag = r.json["result"]
        self.assertEqual(type(tag), dict)

        # Check data
        self.assertEqual(len(tag), 3)
        self.assertIn("id", tag)
        self.assertIn("name", tag)
        self.assertIn("color", tag)

        self.assertEqual(tag["id"], tag_id)
        self.assertEqual(tag["name"], t["name"])
        self.assertEqual(tag["color"], t["color"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Tag resource.

        This test tries to get the data of a tag without providing the access
        token, which shouldn't work.
        """
        # Get the tag with ID 1 (which doesn't exist) without providing the
        # acess token.
        r = self.client.get("/tag/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Tag resource.

        This test tries to get the data of some tag providing an invalid access
        token, which shouldn't work.
        """
        # Get the tag with ID 1 (which doesn't exist) providing an invalid
        # access token ("1234").
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/tag/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the Tag resource.

        This test tries to get a tag of a user from another user, which
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get tag
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get(f"/tag/{tag_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_tag_not_found(self):
        """Test the Get method of the Tag resource.

        This test tries to get a tag that doesn't exist, which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Get tag
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/tag/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag, which should work.
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

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#ffffff"}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        tag_id = r.json["result"]
        self.assertEqual(type(tag_id), int)

    def test_post_missing_access_token(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag without providing the access token,
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", json=t)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag providing an invalid access token,
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

        # Create a tag providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_missing_fields(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag with some mandatory field missing,
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

        # Create tag (without data)
        r = self.client.post("/tag", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create tag (without name)
        t = {"notebook_id": notebook_id}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_invalid_fields(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag providing some invalid/unexpected
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
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Create a tag with an invalid field ("invalid_field")
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "invalid_field": 1}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_notebook_user_unauthorized(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag for a notebook that doesn't belong to
        the request user, which shouldn't work.
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

        # Create tag
        headers = {"Authorization": f"Bearer {access_token}"}
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post_notebook_not_found(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag for a notebook that doesn't exist,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a tag for the notebook with ID 1 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        t = {"notebook_id": 1, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post_tag_exists(self):
        """Test the Post method of the Tag resource.

        This test tries to create a tag with the same name of an existing tag
        in the same notebook, which shouldn't work.
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

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#ff0000"}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#00ff00"}
        r = self.client.post("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag, which should work.
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

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#ffffff"}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        tag_id = r.json["result"]
        self.assertEqual(type(tag_id), int)

    def test_put_edit(self):
        """Test the Put method of the Tag resource.

        This test tries to edit one of the tags of one of the request user's
        notebooks, which should work.
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

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag 1",
            "color": "#ff0000"}
        r = self.client.put("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Edit tag
        new_tag = {"name": "Test Tag 2", "color": "#00ff00"}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get tag
        r = self.client.get(f"/tag/{tag_id}", headers=headers)
        tag = r.json["result"]

        # Check tag
        self.assertEqual(len(tag), 3)

        for i in ("id", "name", "color"):
            self.assertIn(i, tag)

        self.assertEqual(tag["id"], tag_id)
        self.assertEqual(tag["name"], new_tag["name"])
        self.assertEqual(tag["color"], new_tag["color"])

    def test_put_new_missing_access_token(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag without providing the access token,
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put("/tag", json=t)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_edit_missing_access_token(self):
        """Test the Put method of the Tag resource.

        This test tries to edit a tag without providing the access token, which
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
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag 1",
            "color": "#ff0000"}
        r = self.client.put("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Edit tag
        new_tag = {"name": "Test Tag 2", "color": "#00ff00"}
        r = self.client.put(f"/tag/{tag_id}", json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_new_invalid_access_token(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag providing an invalid access token,
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

        # Create tag providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the Tag resource.

        This test tries to edit a tag providing an invalid access token, which
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
        n = {"name": "Test Notebook"}
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag 1",
            "color": "#ff0000"}
        r = self.client.put("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Edit tag providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        new_tag = {"name": "Test Tag 2", "color": "#00ff00"}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_new_missing_fields(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag with some mandatory field missing,
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

        # Create tag (without data)
        r = self.client.put("/tag", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create tag (without name)
        t = {"notebook_id": notebook_id}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_notebook(self):
        """Test the Put method of the Notebook resource.

        This test tries to edit a tag specifying its notebook, which shouldn't
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
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Edit tag
        new_tag = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_invalid_fields(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag providing some invalid/unexpected
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
        r = self.client.post("/notebook", headers=headers, json=n)
        notebook_id = r.json["result"]

        # Create a tag with an invalid field ("invalid_field")
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "invalid_field": 1}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_invalid_fields(self):
        """Test the Put method of the Tag resource.

        This test tries to edit a tag providing some invalid/unexpected field,
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Edit tag with an invalid field ("invalid_field")
        new_tag = {"name": "Test Tag", "invalid_field": 1}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_notebook_user_unauthorized(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag for a notebook that doesn't belong to
        the request user, which shouldn't work.
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

        # Create tag
        headers = {"Authorization": f"Bearer {access_token}"}
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_new_notebook_not_found(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag for a notebook that doesn't exist,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.admin["username"],
            "password": self.admin["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create a tag for the notebook with ID 1 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        t = {"notebook_id": 1, "name": "Test Tag"}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_edit_user_unauthorized(self):
        """Test the Put method of the Tag resource.

        This test tries to edit a tag of a notebook that doesn't belong to the
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.put("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Edit tag
        headers = {"Authorization": f"Bearer {access_token}"}
        new_tag = {"name": "Test Tag 2"}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_new_tag_exists(self):
        """Test the Put method of the Tag resource.

        This test tries to create a tag with the same name of an existing tag
        in the same notebook of the request user, which shouldn't work.
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

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#ff0000"}
        self.client.put("/tag", headers=headers, json=t)

        # Create tag
        t = {
            "notebook_id": notebook_id, "name": "Test Tag", "color": "#00ff00"}
        r = self.client.put("/tag", headers=headers, json=t)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_tag_exists(self):
        """Test the Put method of the Tag resource.

        This test tries to edit a tag with the same name that it currently has
        (which should work) and tries to edit a tag with the same name of
        another existing tag in the same notebook, which shouldn't work.
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

        # Create tags
        t1 = {"notebook_id": notebook_id, "name": "Test Tag 1"}
        t2 = {"notebook_id": notebook_id, "name": "Test Tag 2"}

        r = self.client.put("/tag", headers=headers, json=t1)
        tag_id = r.json["result"]

        self.client.put("/tag", headers=headers, json=t2)

        # Edit tag with its same name
        new_tag = {"name": "Test Tag"}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Edit tag with the same name of the other tag
        new_tag = {"name": "Test Tag 2"}
        r = self.client.put(f"/tag/{tag_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_delete(self):
        """Test the Delete method of the Tag resource.

        This test creates a tag and then tries to delete it, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Create notebook
        headers = {"Authorization": f"Bearer {access_token}"}
        nb = {"name": "Test Notebook"}
        r = self.client.put("/notebook", headers=headers, json=nb)
        notebook_id = r.json["result"]

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Get notebook tag list
        r = self.client.get(f"/tags/{notebook_id}", headers=headers)
        tags = r.json["result"]

        # Check list
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]["id"], tag_id)
        self.assertEqual(tags[0]["name"], t["name"])

        # Create a note with the tag
        n = {
            "notebook_id": notebook_id,
            "title": "Test Note",
            "tags": [t["name"]]}
        r = self.client.post("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Delete tag
        r = self.client.delete(f"/tag/{tag_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get notebook tag list
        r = self.client.get(f"/tags/{notebook_id}", headers=headers)
        tags = r.json["result"]

        # Check list
        self.assertEqual(len(tags), 0)

        # Check that the note doesn't have now the tag
        r = self.client.get(f"/note/{note_id}", headers=headers)
        tags = r.json["result"]["tags"]
        self.assertEqual(len(tags), 0)

    def test_delete_missing_access_token(self):
        """Test the Delete method of the Tag resource.

        This test tries to delete an existing tag without providing the access
        token, which shouldn't work.
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Delete tag
        r = self.client.delete(f"/tag/{tag_id}")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the Tag resource.

        This test tries to delete a tag providing an invalid access token,
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Delete tag providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.delete(f"/tag/{tag_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_delete_unauthorized_user(self):
        """Test the Delete method of the Tag resource.

        This test tries to delete a tag of a user different than the request
        user, which shouldn't work.
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

        # Create tag
        t = {"notebook_id": notebook_id, "name": "Test Tag"}
        r = self.client.post("/tag", headers=headers, json=t)
        tag_id = r.json["result"]

        # Log in as another user
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete tag
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete(f"/tag/{tag_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete_tag_not_found(self):
        """Test the Delete method of the Tag resource.

        This test tries to delete a tag that doesn't exist, which shouldn't
        work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]

        # Delete the tag with ID 1 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.delete("/tag/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":
    unittest.main()
