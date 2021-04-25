"""Tag resources unit tests."""

import unittest
import common


class TagListTestCase(common.BaseTestCase):
    """Notebook List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Tag List resource.

        This test logs in as some user, creates a notebook with some tags and
        then tries to get the notebook's tag list, which should work.
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

        tags = [
            {"notebook_id": notebook_id, "name": "Test Tag 1"},
            {"notebook_id": notebook_id, "name": "Test Tag 2"}]

        for t in tags:
            # Create tag in the notebook
            r = self.client.post("/tag", headers=headers, json=t)

            # Check status code
            self.assertEqual(r.status_code, 201)

            # Check result
            self.assertIn("result", r.json)
            tag_id = r.json["result"]
            self.assertEqual(type(tag_id), int)

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

        This test tries to get the tag list of a notebook that the request user
        doesn't have, which shouldn't work.
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

        # Get the tag list of the notebook with ID 1 (which doesn't exist)
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/tags/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_missing_notebook_id(self):
        """Test the Get method of the Tag List resource.

        This test tries to get the tag list of a notebook without providing the
        notebook ID, which shouldn't work.
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

        # Get the tag list without providing the notebook ID
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self.client.get("/tags", headers=headers)

        # Check status code
        print(r.json)
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


if __name__ == "__main__":
    unittest.main()
