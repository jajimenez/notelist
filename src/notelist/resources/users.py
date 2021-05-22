"""Module with the user resources."""

import hashlib as hl

from flask import request
from werkzeug.security import safe_str_cmp
from flask_restx import Resource, fields
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt,
    get_jwt_identity)
from notelist.apis import auth_api, users_api
from notelist.models.users import User
from notelist.schemas.users import UserSchema
from notelist.resources import (
    Response, VALIDATION_ERROR, USER_UNAUTHORIZED, get_response_data,
    get_response_codes)
from notelist import tools


USER_LOGGED_IN = "User logged in."
TOKEN_REFRESHED = "Token refreshed."
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


@auth_api.route("/login")
class LoginResource(Resource):
    """User login resource."""

    fields = auth_api.model(
        "Login", {
            "username": fields.String(required=True),
            "password": fields.String(required=True)})

    @auth_api.expect(fields)
    @auth_api.doc(
        responses=get_response_codes(200, 400, 401))
    def post(self) -> Response:
        """Log in.

        This operation returns a fresh access token and a refresh token. Any of
        the tokens can be provided to an API request in the following header:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message, the access token and the refresh
        token.
        """
        # Request data
        data = request.get_json() or {}

        # Validate request data
        fields = ["username", "password"]

        inv_fields = ", ".join(
            [i for i in data.keys() if i not in fields] + [
                i for i in fields if (
                    i not in data or type(data[i]) != str or
                    not data[i].strip())])

        if inv_fields:
            return get_response_data(VALIDATION_ERROR.format(inv_fields)), 400

        # We get the hash of the request password, as passwords are stored
        # encrypted in the database.
        user = User.get_by_username(data[fields[0]].strip())
        req_pw = tools.get_hash(data[fields[1]].strip())

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


@auth_api.route("/refresh")
class TokenRefreshResource(Resource):
    """Token refresh resource."""

    @jwt_required(refresh=True)
    @auth_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 422))
    def get(self) -> Response:
        """Get a new, not fresh, access token.

        This operation requires the following header with a refresh token:
            "Authorization" = "Bearer refresh_token"

        :return: Dictionary with the message and the new token.
        """
        # Get the request JWT Identity, which in this application is equal to
        # the ID of the request user.
        uid = get_jwt_identity()

        # Create a new, not fresh, access token
        result = {"access_token": create_access_token(uid, fresh=False)}

        return get_response_data(TOKEN_REFRESHED, result), 200


@auth_api.route("/logout")
class LogoutResource(Resource):
    """User logout resource."""

    @jwt_required()
    @auth_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 422))
    def get(self) -> Response:
        """Log out.

        This operation revokes an access token provided in the request. This
        operation requires the following header with the access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message.
        """
        # JWT payload data
        jti = get_jwt()["jti"]  # JTI (unique identifier)

        # Add the JTI of the JWT of the current request to the Block List in
        # order to revoke the JWT.
        blocklist.add(jti)

        return get_response_data(USER_LOGGED_OUT), 200


@users_api.route("/users")
class UserListResource(Resource):
    """User list resource."""

    @jwt_required()
    @users_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def get(self) -> Response:
        """Get all existing users.

        This operation requires administrator permissions and the following
        header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the users data.
        """
        # JWT payload data
        admin = get_jwt()["admin"]

        # Check permissions
        if not admin:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Get all users
        users = User.get_all()

        c = len(users)
        m = USERS_RETRIEVED_1 if c == 1 else USERS_RETRIEVED_N.format(c)

        return get_response_data(m, user_list_schema.dump(users)), 200


@users_api.route("/user")
class NewUserResource(Resource):
    """New users resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = users_api.model(
        "NewUser", {
            "username": fields.String(required=True),
            "password": fields.String(required=True),
            "admin": fields.Boolean(default=False),
            "enabled": fields.Boolean(default=False),
            "name": fields.String(default=None),
            "email": fields.String(default=None)})

    def _create_user(self) -> Response:
        """Create a new user.

        :return: Dictionary with the message and the user ID.
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
        user.username = user.username.strip()

        if not user.username:
            return get_response_data(VALIDATION_ERROR.format("username")), 400

        # Check if the user already exists (based on its username)
        if User.get_by_username(user.username):
            return get_response_data(USER_EXISTS), 400

        # Save the user
        user.save()

        return get_response_data(USER_CREATED, user.id), 201

    @jwt_required()
    @users_api.expect(req_fields)
    @users_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 403, 422))
    def post(self) -> Response:
        """Create a new user.

        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the user ID.
        """
        return self._create_user()

    @jwt_required()
    @users_api.expect(req_fields)
    @users_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 403, 422))
    def put(self) -> Response:
        """Create a new user.

        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the user ID.
        """
        return self._create_user()


@users_api.route("/user/<int:user_id>")
@users_api.doc(params={"user_id": "User ID (integer)"})
class ExistingUserResource(Resource):
    """Existing users resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = users_api.model(
        "ExistingUser", {
            "username": fields.String,
            "password": fields.String,
            "admin": fields.Boolean,
            "enabled": fields.Boolean,
            "name": fields.String,
            "email": fields.String})

    @jwt_required()
    @users_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 404, 422))
    def get(self, user_id: int) -> Response:
        """Get an existing user's data.

        The user can call this operation only for their own data, unless they
        are an administrator. This operation requires the following header with
        an access token:
            "Authorization" = "Bearer access_token"

        :param user_id: User ID.
        :return: Dictionary with the message and the user data.
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
    @users_api.expect(req_fields)
    @users_api.doc(
        security="apikey",
        responses=get_response_codes(200, 400, 401, 403, 404, 422))
    def put(self, user_id: int) -> Response:
        """Edit an existing user.

        The user, if they aren't an administrator, can call this operation only
        to update their own data, except the "username", "admin" or "enabled"
        fields. This operation requires the following header with an access
        token:
            "Authorization" = "Bearer access_token"

        :param user_id: User ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        jwt = get_jwt()
        uid = jwt["user_id"]
        admin = jwt["admin"]

        # Request data
        data = request.get_json() or {}

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
                type(data["username"]) != str or
                not data["username"].strip()
            ):
                return get_response_data(
                    VALIDATION_ERROR.format("username")), 400

            data["username"] = data["username"].strip()

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

        # Save user
        user.save()

        return get_response_data(USER_UPDATED), 200

    @jwt_required(fresh=True)
    @users_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 404, 422))
    def delete(self, user_id: int) -> Response:
        """Delete an existing user.

        This operation requires administrator permissions and the following
        header with a fresh access token:
            "Authorization" = "Bearer fresh_access_token"

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
