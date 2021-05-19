"""Search resources unit tests."""

import unittest
import common


class SearchTestCase(common.BaseTestCase):
    """Search resource unit tests."""

    def test_get(self):
        """Test the Get method of the Search resource.

        This test searches for some strings, which should work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Create notebooks
        n = {"name": "Work"}
        r = self.client.post("/notebook", headers=headers, json=n)
        nb1_id = r.json["result"]

        n = {"name": "Home"}
        r = self.client.post("/notebook", headers=headers, json=n)
        nb2_id = r.json["result"]

        # Create tags
        t = {"notebook_id": nb1_id, "name": "Python"}
        self.client.post("/tag", headers=headers, json=t)

        t = {"notebook_id": nb2_id, "name": "Work"}
        self.client.post("/tag", headers=headers, json=t)

        # Create notes
        n = {
            "notebook_id": nb1_id,
            "title": "Develop application",
            "tags": ["Python"]}
        self.client.post("/note", headers=headers, json=n)

        n = {
            "notebook_id": nb1_id,
            "title": "Test Python script",
            "tags": []}
        self.client.post("/note", headers=headers, json=n)

        n = {
            "notebook_id": nb2_id,
            "title": "Do shopping",
            "tags": []}
        self.client.post("/note", headers=headers, json=n)

        # Search for "home"
        r = self.client.get("/search/home", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        result = r.json["result"]
        res_notebooks = result["notebooks"]
        res_tags = result["tags"]
        res_notes = result["notes"]

        self.assertEqual(len(res_notebooks), 1)
        self.assertEqual(len(res_tags), 0)
        self.assertEqual(len(res_notes), 0)

        # Search for "APP"
        r = self.client.get("/search/APP", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        result = r.json["result"]
        res_notebooks = result["notebooks"]
        res_tags = result["tags"]
        res_notes = result["notes"]

        self.assertEqual(len(res_notebooks), 0)
        self.assertEqual(len(res_tags), 0)
        self.assertEqual(len(res_notes), 1)

        # Search for "python"
        r = self.client.get("/search/python", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        result = r.json["result"]
        res_notebooks = result["notebooks"]
        res_tags = result["tags"]
        res_notes = result["notes"]

        self.assertEqual(len(res_notebooks), 0)
        self.assertEqual(len(res_tags), 1)
        self.assertEqual(len(res_notes), 2)

    def test_get_missing_access_token(self):
        """Test the Get method of the Search resource.

        This test tries to search for a string without providing the access
        token, which shouldn't work.
        """
        # Search for "python"
        r = self.client.get("/search/python")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Search resource.

        This test tries to search for a string providing an invalid access
        token, which shouldn't work.
        """
        # Search for "python" providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/search/python", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_invalid_search(self):
        """Test the Get method of the Search resource.

        This test tries to search for a string which length is lower than 2,
        which shouldn't work.
        """
        # Log in
        data = {
            "username": self.reg1["username"],
            "password": self.reg1["password"]}
        r = self.client.post("/login", json=data)
        access_token = r.json["result"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Search for "p"
        r = self.client.get("/search/p", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post(self):
        """Test the Post method of the Search resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/search/python")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_put(self):
        """Test the Put method of the Search resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/search/python")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Search resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/search/python")

        # Check status code
        self.assertEqual(r.status_code, 405)


if __name__ == "__main__":
    unittest.main()
