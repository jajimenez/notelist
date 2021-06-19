"""About resources unit tests."""

import unittest
import common


class AboutTestCase(common.BaseTestCase):
    """About resource unit tests."""

    def test_get_ok(self):
        """Test the Get method of the About resource.

        This test tries to call the Get method, which should work.
        """
        r = self.client.get("/about")

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        result = r.json["result"]
        self.assertEqual(type(result), dict)
        self.assertEqual(len(result), 3)

        for i in ("name", "version", "description"):
            self.assertIn(i, result)
            self.assertEqual(type(i), str)

    def test_post_error(self):
        """Test the Post method of the About resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/about")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_put_error(self):
        """Test the Put method of the About resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/about")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete_error(self):
        """Test the Delete method of the About resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/about")

        # Check status code
        self.assertEqual(r.status_code, 405)


if __name__ == "__main__":
    unittest.main()
