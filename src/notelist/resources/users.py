"""Module with the user resources."""

from flask import request
from flask_restful import Resource

from models.users import User
from schemas.users import UserSchema
from resources import get_response_data


USERS_RETRIEVED_1 = "1 user retrieved."
USERS_RETRIEVED_N = "{} users retrieved."
USER_RETRIEVED = "User retrieved."
USER_CREATED = "User created."
USER_UPDATED = "User updated."
USER_DELETED = "User deleted."
USER_NOT_FOUND = "User not found."
USER_EXISTS = "User already exists."
INVALID_PASSWORD = "Invalid password. It must have 4-100 characters."


user_list_schema = UserSchema(many=True)
user_schema = UserSchema()


class UserListResource(Resource):
    """User List resource."""

    def get(self):
        """Handle a User List Get request.

        Return all the users.
        """
        users = User.get_all()
        count = len(users)

        if count == 1:
            message = USERS_RETRIEVED_1
        else:
            message = USERS_RETRIEVED_N.format(count)

        return get_response_data(message, user_list_schema.dump(users)), 200


class UserResource(Resource):
    """User resource."""

    def get(self, username: int):
        """Handle a User Get request.

        Return the user with the given username.

        :param username: Username.
        """
        user = User.get_by_username(username)

        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        return get_response_data(USER_RETRIEVED, user_schema.dump(user)), 200

    def post(self, username: str):
        """Handle a User Post request.

        Save a new user with the given username and data.

        :param username: Username.
        """
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

        user.save()
        return get_response_data(USER_CREATED), 201

    def put(self, username: str):
        """Handle a User Put request.

        Save a new or existing user with the given username and data.

        :param username: Username.
        """
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

        user.save()
        return get_response_data(message), code

    def delete(self, username: str):
        """Handle a User Delete request.

        Delete an existing user given its username.

        :param username: Username.
        """
        user = User.get_by_username(username)

        if not user:
            return get_response_data(USER_NOT_FOUND), 404

        user.delete()
        return get_response_data(USER_DELETED), 200
