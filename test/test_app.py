"""Application unit tests."""

import unittest
import common


class AppTestCase(common.BaseTestCase):
    """Application unit tests."""

    def test_endpoints(self):
        """Test endpoints."""
        r = self.client.get("/")
        assert r.status_code == 200


if __name__ == "__main__":
    unittest.main()
