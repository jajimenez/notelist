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

        # Create a notebook
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
        # Get the data of the tag with ID 1 (which doesn't exist)
        r = self.client.get("/tag/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Tag resource.

        This test tries to get the data of some tag providing an invalid access
        token, which shouldn't work.
        """
        # Get data providing an invalid access token ("1234")
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

        # Create a notebook
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


if __name__ == "__main__":
    unittest.main()
