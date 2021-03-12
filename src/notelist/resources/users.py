"""Module with the user resources."""

import hashlib as hl

from flask import request
from werkzeug.security import safe_str_cmp
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt,
    get_jwt_identity)

from notelist.models.users import User
from notelist.schemas.users import UserSchema
from notelist.resources import get_response_data, Response
from notelist import tools


USER_UNAUTHORIZED = "User unauthorized."
USERS_RETRIEVED_1 = "1 user retrieved."
USERS_RETRIEVED_N = "{} users retrieved."
USER_RETRIEVED = "User retrieved."
USER_CREATED = "User created."
USER_UPDATED = "User updated."
USER_DELETED = "User deleted."
USER_NOT_FOUND = "User not found."
USER_EXISTS = "User already exists."
INVALID_PASSWORD = "Invalid password. It must have 4-100 characters."
USER_LOGGED_IN = "User logged in."
INVALID_CREDENTIALS = "Invalid credentials."
USER_LOGGED_OUT = "User logged out."


user_list_schema = UserSchema(many=True)
user_schema = UserSchema()
blocklist = set()


class UserListResource(Resource):
    """User List resource."""

    @jwt_required()
    def get(self) -> Response:
        """Handle a User List Get request.

        Return all the users. This endpoint requires administrator permissions.
        """
        # Check permissions
        if not get_jwt()["admin"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        users = User.get_all()
        count = len(users)

        if count == 1:
            message = USERS_RETRIEVED_1
        else:
            message = USERS_RETRIEVED_N.format(count)

        return get_response_data(message, user_list_schema.dump(users)), 200


class UserResource(Resource):
    """User resource."""

    @jwt_required()
    def get(self, username: int) -> Response:
        """Handle a User Get request.

        Return the user with the given username. The current request user can
        only call this endpoint for their own user, unless it's an
        administrator.

        :param username: Username.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data

        if not jwt["admin"] and username != jwt["username"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        user = User.get_by_username(username)

        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        return get_response_data(USER_RETRIEVED, user_schema.dump(user)), 200

    @jwt_required()
    def post(self, username: str) -> Response:
        """Handle a User Post request.

        Save a new user with the given username and data. This endpoint
        requires administrator permissions.

        :param username: Username.
        """
        # Check permissions
        if not get_jwt()["admin"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        data = request.get_json()

        # We set the username as the one provided in the request URL,
        # overwriting the username value in the request body (if any).
        data["username"] = username
        user = user_schema.load(data)

        # Check if the user already exists
        if User.get_by_username(user.username):
            return get_response_data(USER_EXISTS), 400

        # Validate password length
        if len(user.password) < 4:
            return get_response_data(INVALID_PASSWORD), 400

        # We get the hash of the password, to store the password encrypted in
        # the database.
        user.password = tools.get_hash(user.password)

        user.save()
        return get_response_data(USER_CREATED), 201

    @jwt_required()
    def put(self, username: str) -> Response:
        """Handle a User Put request.

        Save a new or existing user with the given username and data. This
        endpoint requires administrator permissions.

        :param username: Username.
        """
        # Check permissions
        if not get_jwt()["admin"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        user = User.get_by_username(username)
        data = request.get_json()

        if user:  # The user already exists, so we update it.
            if "username" in data:
                # Check if the value of the username is new and if there is
                # another existing user with the same username.
                if (
                    data["username"] != username and
                    User.get_by_username(data["username"])
                ):
                    return get_response_data(USER_EXISTS), 400

                user.username = data["username"]

            if "password" in data:
                user.password = data["password"]

            if "enabled" in data:
                user.enabled = data["enabled"]

            if "admin" in data:
                user.admin = data["admin"]

            if "name" in data:
                user.name = data["name"]

            if "email" in data:
                user.email = data["email"]

            message = USER_UPDATED
            code = 200
        else:  # The user doesn't exist, so we create it.
            data["username"] = username
            user = user_schema.load(data)

            message = USER_CREATED
            code = 201

        # Validate password length
        if len(user.password) < 4:
            return get_response_data(INVALID_PASSWORD), 400

        # We get the hash of the password, to store the password encrypted in
        # the database.
        user.password = tools.get_hash(user.password)

        user.save()
        return get_response_data(message), code

    @jwt_required(fresh=True)
    def delete(self, username: str) -> Response:
        """Handle a User Delete request.

        Delete an existing user given its username. This endpoint requires
        administrator permissions.

        :param username: Username.
        """
        # Check permissions
        if not get_jwt()["admin"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        user = User.get_by_username(username)

        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        user.delete()
        return get_response_data(USER_DELETED), 200


class LoginResource(Resource):
    """User Login resource."""

    def post(self) -> Response:
        """Handle a Login Post request."""
        req_user = user_schema.load(request.get_json())
        user = User.get_by_username(req_user.username)

        # We get the hash of the request password, as passwords are stored
        # encrypted in the database.
        req_pw = tools.get_hash(req_user.password)

        if user and safe_str_cmp(req_pw, user.password):
            # The user ID is the Identity of the tokens (not to be confused
            # with the JTI (unique identifier) of the tokens).
            result = {
                "access_token": create_access_token(user.id, fresh=True),
                "refresh_token": create_refresh_token(user.id)}

            return get_response_data(USER_LOGGED_IN, result), 200

        return get_response_data(INVALID_CREDENTIALS), 401


class TokenRefreshResource(Resource):
    """Token Refresh resource."""

    @jwt_required(refresh=True)
    def post(self) -> Response:
        """Handle a Token Refresh Post request."""
        user_id = get_jwt_identity()

        # New, not fresh, access token
        result = {"access_token": create_access_token(user_id, fresh=False)}
        return get_response_data(USER_LOGGED_IN, result), 200


class LogoutResource(Resource):
    """Logout resource."""

    @jwt_required()
    def post(self) -> Response:
        """Handle a Logout Post request."""
        # Add the JTI (unique identifier) of the JWT of the current request
        # to the Block List in order to revoke the JWT.
        jti = get_jwt()["jti"]
        blocklist.add(jti)

        return get_response_data(USER_LOGGED_OUT), 200
