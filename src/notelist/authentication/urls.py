"""Notelist - Authentication - URLs."""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from authentication.views import RevokeTokenView


app_name = "authentication"

urlpatterns = [
    path("get-token/", obtain_auth_token, name="get-token"),
    path("revoke-token/", RevokeTokenView.as_view(), name="revoke-token"),
]
