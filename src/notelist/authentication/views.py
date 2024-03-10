"""Notelist - Authentication - Views."""

from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED


class RevokeTokenView(APIView):
    """View for revoking the authentication token of the current user."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle a GET request."""
        try:
            # Delete the token of the current user
            Token.objects.get(user=request.user).delete()

            status_code = HTTP_200_OK
            message = "Token revoked."
        except Token.DoesNotExist:
            status_code = HTTP_401_UNAUTHORIZED
            message = "Invalid token."

        return Response(status=status_code, data={"message": message})
