"""Notelist - Authentication - Tests."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)


get_token_url = reverse("authentication:get-token")
revoke_token_url = reverse("authentication:revoke-token")


class AuthenticationTests(TestCase):
    """Authentication API tests."""

    def setUp(self):
        """Set up the tests."""
        # Create user
        self.user_model = get_user_model()

        self.user_username = "user"
        self.user_password = "password"

        self.user = self.user_model.objects.create_user(
            username=self.user_username, password=self.user_password
        )

        # Create test client
        self.client = APIClient()

    def test_get_token(self):
        """Test getting an authentication token given a valid username and
        password.
        """
        # Check that the user doesn't have a token
        query = Token.objects.filter(user=self.user)
        self.assertFalse(query.exists())

        # Make HTTP request for getting the token
        data = {"username": self.user_username, "password": self.user_password}
        response = self.client.post(get_token_url, data)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_200_OK)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("token", data)

        token = data["token"]

        self.assertIs(type(token), str)
        self.assertEqual(len(token), 40)

        # Check that the user has a token and it's the same as the one from the
        # response.
        self.assertTrue(query.exists())
        self.assertEqual(query.first().key, token)

    def test_get_token_multiple_times(self):
        """Test getting an authentication token given the same username and
        password multiple times.
        """
        # Make HTTP requests for getting the token
        data = {"username": self.user_username, "password": self.user_password}

        r1 = self.client.post(get_token_url, data)
        r2 = self.client.post(get_token_url, data)

        # Check that the tokens are the same
        self.assertEqual(r1.json()["token"], r2.json()["token"])

    def test_get_token_invalid_methods(self):
        """Test getting an authentication token using invalid HTTP methods."""
        # Make HTTP requests for getting the token
        data = {"username": self.user_username, "password": self.user_password}

        r1 = self.client.get(get_token_url, data)
        r2 = self.client.put(get_token_url, data)
        r3 = self.client.patch(get_token_url, data)
        r4 = self.client.delete(get_token_url, data)

        for r, m in ((r1, "GET"), (r2, "PUT"), (r3, "PATCH"), (r4, "DELETE")):
            # Check response status code
            self.assertEqual(r.status_code, HTTP_405_METHOD_NOT_ALLOWED)

            # Check response data
            data = r.json()

            self.assertIs(type(data), dict)
            self.assertEqual(len(data), 1)
            self.assertIn("detail", data)
            self.assertEqual(data["detail"], f'Method "{m}" not allowed.')

    def test_get_token_no_username_and_password(self):
        """Test getting an authentication token without providing the username
        and the password.
        """
        # Make HTTP request for getting the token
        response = self.client.post(get_token_url)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 2)

        for i in ("username", "password"):
            self.assertIn(i, data)
            self.assertEqual(data[i], ["This field is required."])

    def test_get_token_no_username(self):
        """Test getting an authentication token without providing the username."""
        # Make HTTP request for getting the token
        data = {"password": self.user_password}
        response = self.client.post(get_token_url, data)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("username", data)
        self.assertEqual(data["username"], ["This field is required."])

    def test_get_token_no_password(self):
        """Test getting an authentication token without providing the password."""
        # Make HTTP request for getting the token
        data = {"username": self.user_username}
        response = self.client.post(get_token_url, data)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("password", data)
        self.assertEqual(data["password"], ["This field is required."])

    def test_get_token_invalid_user(self):
        """Test getting an authentication token given a username that doesn't
        exist.
        """
        # Make HTTP request for getting the token
        data = {"username": "invalid", "password": self.user_password}
        response = self.client.post(get_token_url, data)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("non_field_errors", data)

        self.assertEqual(
            data["non_field_errors"],
            ["Unable to log in with provided credentials."],
        )

    def test_revoke_token(self):
        """Test revoking the authentication token of the request user."""
        # Make HTTP request for getting the token
        data = {"username": self.user_username, "password": self.user_password}
        response = self.client.post(get_token_url, data)
        token = response.json()["token"]

        # Check that the user has a token
        query = Token.objects.filter(user=self.user)
        self.assertTrue(query.exists())

        # Make HTTP request for revoking the token
        headers = {"Authorization": f"Token {token}"}
        response = self.client.get(revoke_token_url, headers=headers)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_200_OK)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Token revoked.")

        # Check that the user doesn't have a token
        self.assertFalse(query.exists())

    def test_revoke_token_invalid_token(self):
        """Test revoking the authentication token of the request user when it
        has already been revoked."""
        # Make HTTP request for getting the token
        data = {"username": self.user_username, "password": self.user_password}
        response = self.client.post(get_token_url, data)
        token = response.json()["token"]

        # Check that the user has a token
        query = Token.objects.filter(user=self.user)
        self.assertTrue(query.exists())

        # Make 2 HTTP requests for revoking the token
        headers = {"Authorization": f"Token {token}"}
        self.client.get(revoke_token_url, headers=headers)
        response = self.client.get(revoke_token_url, headers=headers)

        # Check the status code of the second response
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

        # Check the response data of the second response
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Invalid token.")

        # Check that the user doesn't have a token
        self.assertFalse(query.exists())

    def test_revoke_token_unauthenticated(self):
        """Test revoking the authentication token of the request user without
        providing the token in the request headers."""
        # Make HTTP request for revoking the token
        response = self.client.get(revoke_token_url)

        # Check response status code
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

        # Check response data
        data = response.json()

        self.assertIs(type(data), dict)
        self.assertEqual(len(data), 1)
        self.assertIn("detail", data)

        self.assertEqual(
            data["detail"], "Authentication credentials were not provided."
        )
