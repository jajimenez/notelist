"""Module with the user resources."""

import hashlib as hl

from flask import request
from werkzeug.security import safe_str_cmp
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, \
    create_refresh_token, get_jwt, get_jwt_identity

from notelist.models.users import User
from notelist.schemas.users import UserSchema
from notelist.resources import Response, OPERATION_NOT_ALLOWED, \
    USER_UNAUTHORIZED, get_response_data
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
MIN_PASSWORD = 8
MAX_PASSWORD = 100
INVALID_PASSWORD = "Invalid password. It must have 8-100 characters."


user_list_schema = UserSchema(many=True)
user_schema = UserSchema()
blocklist = set()


class LoginResource(Resource):
    """User Login resource."""

    def post(self) -> Response:
        """Handle a Login Post request.

        :return: Dictionary with the message.
        """
        data = request.get_json()
        u = "username"
        p = "password"

        # Check request data
        for i in (u, p):
            if i not in data or type(data[i]) != str or data[i] == "":
                return get_response_data(INVALID_CREDENTIALS), 401

        # We get the hash of the request password, as passwords are stored
        # encrypted in the database.
        req_pw = tools.get_hash(data[p])
        user = User.get_by_username(data[u])

        # Check password
        if user and user.enabled and safe_str_cmp(req_pw, user.password):
            # The user ID is the Identity of the tokens (not to be confused
            # with the JTI (unique identifier) of the tokens).
            result = {
                "access_token": create_access_token(user.id, fresh=True),
                "refresh_token": create_refresh_token(user.id),
                "user_id": user.id}
            return get_response_data(USER_LOGGED_IN, result), 200

        return get_response_data(INVALID_CREDENTIALS), 401


class TokenRefreshResource(Resource):
    """Token Refresh resource."""

    @jwt_required(refresh=True)
    def post(self) -> Response:
        """Handle a Token Refresh Post request.

        :return: Dictionary with the message and a new, not fresh access token.
        """
        user_id = get_jwt_identity()

        # New, not fresh, access token
        result = {"access_token": create_access_token(user_id, fresh=False)}
        return get_response_data(USER_LOGGED_IN, result), 200


class LogoutResource(Resource):
    """Logout resource."""

    @jwt_required()
    def post(self) -> Response:
        """Handle a Logout Post request.

        :return: Dictionary with the message.
        """
        # Add the JTI (unique identifier) of the JWT of the current request
        # to the Block List in order to revoke the JWT.
        jti = get_jwt()["jti"]
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
    def get(self, _id: int) -> Response:
        """Handle a User Get request.

        Return the user with the given ID. The current request user can only
        call this endpoint for their own user, unless they are an
        administrator.

        :param _id: User ID.
        :return: Dictionary with the message and result.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data

        if not jwt["admin"] and jwt["user_id"] != _id:
            return get_response_data(USER_UNAUTHORIZED), 403

        user = User.get_by_id(_id)

        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        return get_response_data(USER_RETRIEVED, user_schema.dump(user)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a User Post request.

        Save a new user with the given data. This endpoint requires
        administrator permissions and creating a user whose username is "root"
        is not allowed.

        :return: Dictionary with the message and the user ID as the result.
        """
        data = request.get_json()

        # Check if the request is either for updating an existing user or for
        # creating a new user whose username is "root".
        if "id" in data or ("username" in data and data["username"] == "root"):
            return get_response_data(OPERATION_NOT_ALLOWED), 403

        # Check permissions
        if not get_jwt()["admin"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        user = user_schema.load(data)

        # Validate password length
        c = len(user.password)

        if c < MIN_PASSWORD or c > MAX_PASSWORD:
            return get_response_data(INVALID_PASSWORD), 400

        # Check if the user already exists
        if User.get_by_username(user.username):
            return get_response_data(USER_EXISTS), 400

        # We get the hash of the password, to store the password encrypted in
        # the database.
        user.password = tools.get_hash(user.password)

        # Save the user
        user.save()

        return get_response_data(USER_CREATED, user.id), 201

    @jwt_required()
    def put(self) -> Response:
        """Handle a User Put request.

        Save a new or existing user with the given data. The request user, if
        they aren't an administrator, can only call this endpoint to update
        their own user's fields, except their "username", "admin" or "enabled"
        fields. Neither creating a user whose username is "root" nor changing
        the "root" user's username are allowed.

        :return: Dictionary with the message and, if the user has been created,
        the user ID as the result.
        """
        jwt = get_jwt()  # JWT payload data
        data = request.get_json()

        # If there isn't any ID in the request data, we create a new user.
        # Otherwise we edit the existing user with the given ID.
        edit = "id" in data

        if edit:  # We edit the existing user
            user = User.get_by_id(data["id"])
            result = False

            if jwt["admin"] and not user:
                return get_response_data(USER_NOT_FOUND), 404

            # Check permissions
            if (
                not jwt["admin"] and (
                    not user or jwt["user_id"] != user.id or "username" in data
                    or "admin" in data or "enabled" in data)
            ):
                return get_response_data(USER_UNAUTHORIZED), 403

            if "username" in data:
                # Check if the value of the username is new
                if data["username"] != user.username:
                    # Check if the new username is "root"
                    if user.username == "root":
                        return get_response_data(OPERATION_NOT_ALLOWED), 403

                    # Check if there is another existing user with the same new
                    # username.
                    if User.get_by_username(data["username"]):
                        return get_response_data(USER_EXISTS), 400

                user.username = data["username"]

            if "password" in data:
                # Validate password length
                c = len(data["password"])

                if c < MIN_PASSWORD or c > MAX_PASSWORD:
                    return get_response_data(INVALID_PASSWORD), 400

                # We get the hash of the password, to store the password
                # encrypted in the database.
                user.password = tools.get_hash(data["password"])

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
        else:  # We create a new user
            # Check permissions
            if not jwt["admin"]:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if the request is for creating a user whose username is
            # "root".
            if "username" in data and data["username"] == "root":
                return get_response_data(OPERATION_NOT_ALLOWED), 403

            # Validate password length
            c = len(data["password"])

            if c < MIN_PASSWORD or c > MAX_PASSWORD:
                return get_response_data(INVALID_PASSWORD), 400

            # We get the hash of the password, to store the password encrypted
            # in the database.
            data["password"] = tools.get_hash(data["password"])

            # We validate the data. If any of the User model required fields is
            # missing, a "marshmallow.ValidationError" exception is raised.
            user = user_schema.load(data)
            result = True

            # Check if there is another existing user with the same username
            if User.get_by_username(user.username):
                return get_response_data(USER_EXISTS), 400

            message = USER_CREATED
            code = 201

        # Save the user
        user.save()
        result = user.id if result else None

        return get_response_data(message, result), code

    @jwt_required(fresh=True)
    def delete(self, _id: int) -> Response:
        """Handle a User Delete request.

        Delete an existing user given its ID. This endpoint requires
        administrator permissions and deleting the "root" user is not allowed.

        :param _id: User ID.
        :return: Dictionary with the message.
        """
        # Check permissions
        if not get_jwt()["admin"]:
            return get_response_data(USER_UNAUTHORIZED), 403

        user = User.get_by_id(_id)

        # Check if the user doesn't exist or is "root"
        if user and user.username == "root":
            return get_response_data(OPERATION_NOT_ALLOWED), 403
        elif not user:
            return get_response_data(USER_NOT_FOUND), 404

        user.delete()
        return get_response_data(USER_DELETED), 200
