"""Module with the user resources."""

import hashlib as hl
from typing import Optional

from flask import request
from werkzeug.security import safe_str_cmp
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, \
    create_refresh_token, get_jwt, get_jwt_identity

from notelist.models.users import User
from notelist.schemas.users import UserSchema
from notelist.resources import Response, VALIDATION_ERROR, USER_UNAUTHORIZED, \
    get_response_data
from notelist import tools


USER_LOGGED_IN = "User logged in."
USER_LOGGED_OUT = "User logged out."
USERS_RETRIEVED_1 = "1 user retrieved."
USERS_RETRIEVED_N = "{} users retrieved."
USER_RETRIEVED = "User retrieved."
USER_CREATED = "User created."
USER_UPDATED = "User updated."
USER_DELETED = "User deleted."
INVALID_CREDENTIALS = "Invalid credentials."
USER_NOT_FOUND = "User not found."
USER_EXISTS = "A user with the same username already exists."
INVALID_PASSWORD = "Invalid password. It must have 8-100 characters."

user_list_schema = UserSchema(many=True)
user_schema = UserSchema()
blocklist = set()


class LoginResource(Resource):
    """User Login resource."""

    def post(self) -> Response:
        """Handle a Login Post request.

        Log in a user.

        :return: Dictionary with the message.
        """
        # Request data
        data = request.get_json() or {}

        # Validate request data
        u = "username"
        p = "password"

        fields = [
            i for i in [u, p]
            if i not in data or type(data[i]) != str or not data[i]]

        if fields:
            return get_response_data(VALIDATION_ERROR.format(fields)), 400

        # We get the hash of the request password, as passwords are stored
        # encrypted in the database.
        req_pw = tools.get_hash(data[p])
        user = User.get_by_username(data[u])

        # Check password
        if user and user.enabled and safe_str_cmp(req_pw, user.password):
            # Create access and refresh tokens. The user ID is the Identity of
            # the tokens (not to be confused with the JTI (unique identifier)
            # of the tokens).
            result = {
                "access_token": create_access_token(user.id, fresh=True),
                "refresh_token": create_refresh_token(user.id),
                "user_id": user.id}
            return get_response_data(USER_LOGGED_IN, result), 200

        return get_response_data(INVALID_CREDENTIALS), 401


class TokenRefreshResource(Resource):
    """Token Refresh resource."""

    @jwt_required(refresh=True)
    def get(self) -> Response:
        """Handle a Token Refresh Get request.

        Get a new, not fresh, access token.

        :return: Dictionary with the message and the new token.
        """
        # Get the request JWT Identity, which in this application is equal to
        # the ID of the request user.
        uid = get_jwt_identity()

        # Create a new, not fresh, access token
        result = {"access_token": create_access_token(uid, fresh=False)}

        return get_response_data(USER_LOGGED_IN, result), 200


class LogoutResource(Resource):
    """Logout resource."""

    @jwt_required()
    def get(self) -> Response:
        """Handle a Logout Get request.

        Log out the request user by revoking the request JWT.

        :return: Dictionary with the message.
        """
        # JWT payload data
        jti = get_jwt()["jti"]  # JTI (unique identifier)

        # Add the JTI of the JWT of the current request to the Block List in
        # order to revoke the JWT.
        blocklist.add(jti)

        return get_response_data(USER_LOGGED_OUT), 200


class UserListResource(Resource):
    """User List resource."""

    @jwt_required()
    def get(self) -> Response:
        """Handle a User List Get request.

        Return all the users. This endpoint requires administrator permissions.

        :return: Dictionary with the message and result.
        """
        # JWT payload data
        admin = get_jwt()["admin"]

        # Check permissions
        if not admin:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Get all the users
        users = User.get_all()

        c = len(users)
        m = USERS_RETRIEVED_1 if c == 1 else USERS_RETRIEVED_N.format(c)

        return get_response_data(m, user_list_schema.dump(users)), 200


class UserResource(Resource):
    """User resource."""

    @jwt_required()
    def get(self, user_id: int) -> Response:
        """Handle a User Get request.

        Return the user with the given ID. The current request user can only
        call this endpoint for their own user, unless they are an
        administrator.

        :param user_id: User ID.
        :return: Dictionary with the message and result.
        """
        # JWT payload data
        jwt = get_jwt()
        uid = jwt["user_id"]
        admin = jwt["admin"]

        # Check permissions
        if not admin and uid != user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Get the user
        user = User.get_by_id(user_id)

        # Check if the user doesn't exist
        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        return get_response_data(USER_RETRIEVED, user_schema.dump(user)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a User Post request.

        Save a new user with the given data. This endpoint requires
        administrator permissions.

        :return: Dictionary with the message and the user ID as the result.
        """
        # JWT payload data
        admin = get_jwt()["admin"]

        # Check permissions
        if not admin:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Request data
        data = request.get_json() or {}

        # We validate the request data. If any of the User model required
        # fields is missing, a "marshmallow.ValidationError" exception is
        # raised.
        user = user_schema.load(data)

        if user.password is None:
            return get_response_data(VALIDATION_ERROR.format("password")), 400

        # Check if the user already exists (based on its username)
        if User.get_by_username(user.username):
            return get_response_data(USER_EXISTS), 400

        # Save the user
        user.save()

        return get_response_data(USER_CREATED, user.id), 201

    @jwt_required()
    def put(self, user_id: Optional[int] = None) -> Response:
        """Handle a User Put request.

        Save a new or existing user with the given data. The request user, if
        they aren't an administrator, can only call this endpoint to update
        their own user's fields, except their "username", "admin" or "enabled"
        fields.

        :param user_id: ID of the user to update or None to create a new user.
        :return: Dictionary with the message and, if the user has been created,
        the user ID as the result.
        """
        # JWT payload data
        jwt = get_jwt()
        uid = jwt["user_id"]
        admin = jwt["admin"]

        # Request data
        data = request.get_json() or {}

        # If "user_id" is None, we create a new user. Otherwise we edit the
        # existing user with the given ID.
        new = user_id is None

        if new:
            # Check permissions
            if not admin:
                return get_response_data(USER_UNAUTHORIZED), 403

            # We validate the request data. If any of the User model required
            # fields is missing, a "marshmallow.ValidationError" exception is
            # raised.
            user = user_schema.load(data)  # It only validates "username"

            if user.password is None:
                return get_response_data(
                    VALIDATION_ERROR.format("password")), 400

            # Check if the user already exists (based on its username)
            if User.get_by_username(user.username):
                return get_response_data(USER_EXISTS), 400

            message = USER_CREATED
            code = 201
        else:
            # Get existing user
            user = User.get_by_id(user_id)

            # Check if the user exists and the permissions. "username", "admin"
            # and "enabled" are the fields that not administrator users aren't
            # allowed to modify.
            if (
                not admin and (
                    not user or uid != user.id or "username" in data
                    or "admin" in data or "enabled" in data)
            ):
                return get_response_data(USER_UNAUTHORIZED), 403
            elif admin and not user:
                return get_response_data(USER_NOT_FOUND), 404

            # Make a copy of the request data
            data = data.copy()

            # Check if a new username is provided and if there is already a
            # user with this username.
            if "username" in data:
                if (
                    data["username"] != user.username and
                    User.get_by_username(data["username"])
                ):
                    return get_response_data(USER_EXISTS), 400
            else:
                data["username"] = user.username

            # Check if new values for "enabled", "admin", "name" or "email" are
            # provided.
            if "enabled" not in data:
                data["enabled"] = user.enabled

            if "admin" not in data:
                data["admin"] = user.admin

            if "name" not in data:
                data["name"] = user.name

            if "email" not in data:
                data["email"] = user.email

            # Check if a new value for the password is provided. If not, we
            # need to temporarily store the current encrypted password and
            # recover it later as "user_schema.load" will encrypt again the
            # password.
            password = user.password if "password" not in data else None

            # We validate the request data. If any provided field is invalid,
            # a "marshmallow.ValidationError" exception is raised.
            new_user = user_schema.load(data)

            # Update user object
            user.username = new_user.username
            user.admin = new_user.admin
            user.enabled = new_user.enabled
            user.name = new_user.name
            user.email = new_user.email
            user.password = password if password else new_user.password

            message = USER_UPDATED
            code = 200

        # Save the user
        user.save()
        result = user.id if new else None

        return get_response_data(message, result), code

    @jwt_required(fresh=True)
    def delete(self, user_id: int) -> Response:
        """Handle a User Delete request.

        Delete an existing user given its ID. This endpoint requires
        administrator permissions.

        :param user_id: User ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        admin = get_jwt()["admin"]

        # Check permissions (only administrator users can delete users)
        if not admin:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Get user
        user = User.get_by_id(user_id)

        # Check if the user doesn't exist
        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        # Delete user
        user.delete()

        return get_response_data(USER_DELETED), 200
