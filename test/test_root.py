"""Root resource unit tests."""

import unittest
import common


class RootTestCase(common.BaseTestCase):
    """Root resource unit tests."""

    def test_get_ok(self):
        """Test the Get method of the Root resource.

        This test tries to call the Get method, which should work.
        """
        r = self.client.get("/")

        # Check status code
        self.assertEqual(r.status_code, 200)

    def test_post_error(self):
        """Test the Post method of the Root resource.

        This test tries to call the Post method, which shouldn't work.
        """
        r = self.client.post("/")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_put_error(self):
        """Test the Put method of the Root resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r = self.client.put("/")

        # Check status code
        self.assertEqual(r.status_code, 405)

    def test_delete_error(self):
        """Test the Delete method of the Root resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r = self.client.delete("/")

        # Check status code
        self.assertEqual(r.status_code, 405)


if __name__ == "__main__":
    unittest.main()
