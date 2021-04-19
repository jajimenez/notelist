"""Module with the notebook resources."""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from notelist.models.notebooks import Notebook
from notelist.schemas.notebooks import NotebookSchema
from notelist.schemas.users import UserSchema
from notelist.schemas.tags import TagSchema
from notelist.resources import Response, USER_UNAUTHORIZED, get_response_data


NOTEBOOK_RETRIEVED_1 = "1 notebook retrieved."
NOTEBOOK_RETRIEVED_N = "{} notebooks retrieved."
NOTEBOOK_RETRIEVED = "Notebook retrieved."
NOTEBOOK_CREATED = "Notebook created."
NOTEBOOK_UPDATED = "Notebook updated."
NOTEBOOK_DELETED = "Notebook deleted."
NOTEBOOK_NOT_FOUND = "Notebook not found."
NOTEBOOK_EXISTS = (
    "Another notebook with the same name already exists for the user.")

notebook_list_schema = NotebookSchema(many=True)
notebook_schema = NotebookSchema()
user_schema = UserSchema()
tag_list_schema = TagSchema(many=True)


class NotebookListResource(Resource):
    """Notebook List resource."""

    @jwt_required()
    def get(self) -> Response:
        """Handle a Notebook List Get request.

        Return all the notebooks of the current user.

        :return: Dictionary with the message and result.
        """
        user_id = get_jwt()["user_id"]
        notebooks = Notebook.get_all_by_user(user_id)
        count = len(notebooks)

        if count == 1:
            message = NOTEBOOK_RETRIEVED_1
        else:
            message = NOTEBOOK_RETRIEVED_N.format(count)

        return get_response_data(
            message, notebook_list_schema.dump(notebooks)), 200


class NotebookResource(Resource):
    """Notebook resource."""

    @jwt_required()
    def get(self, _id: int) -> Response:
        """Handle a Notebook Get request.

        Return the notebook with the given ID. The current request user can
        only call this endpoint for their own notebooks, unless they are an
        administrator.

        :param _id: Notebook ID.
        :return: Dictionary with the message and result.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        n = Notebook.get_by_id(_id)

        if not jwt["admin"] and (not n or jwt["id"] != n.user.id):
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(
            NOTEBOOK_RETRIEVED, notebook_schema.dump(n)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a Notebook Post request.

        Save a new notebook with the given data. The current request user can
        only call this endpoint if the notebook is one of theirs, unless they
        are an administrator.

        :return: Dictionary with the message and the notebook ID as the result.
        """
        # Check that the request is not for updating an existing notebook
        data = request.get_json()

        if "id" in data:
            return get_response_data(OPERATION_NOT_ALLOWED), 403

        # Check permissions
        jwt = get_jwt()  # JWT payload data
        notebook = notebook_schema.load(data)

        if not jwt["admin"] and jwt["id"] != nnotebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Save the notebook
        notebook.save()

        return get_response_data(NOTEBOOK_CREATED, notebook.id), 201

    @jwt_required()
    def put(self) -> Response:
        """Handle a Notebook Put request.

        Save a new or existing notebook with the given data. The current
        request user can only call this endpoint if the notebook is one of
        theirs, unless they are an administrator.

        :return: Dictionary with the message and, if the notebook has been
        created, the notebook ID as the result.
        """
        jwt = get_jwt()  # JWT payload data
        data = request.get_json()

        # If there isn't any ID in the request data, we create a new notebook.
        # Otherwise we edit the existing notebook with the given ID.
        edit = "id" in data

        if edit:  # We edit the existing notebook
            notebook = Notebook.get_by_id(data["id"])
            result = False

            if jwt["admin"] and not notebook:
                return get_response_data(NOTEBOOK_NOT_FOUND), 404

            # Check permissions
            if (
                not jwt["admin"] and (
                    not notebook or jwt["id"] != notebook.user.id
                    or "user_id" in data)
            ):
                return get_response_data(USER_UNAUTHORIZED), 403

            if "name" in data:
                # Check if the value of the name is new and if there is another
                # existing notebook of the same user with the same name.
                if (
                    data["name"] != notebook.name and
                    Notebook.get_by_name(notebook.user.id, data["name"])
                ):
                    return get_response_data(NOTEBOOK_EXISTS), 400

                notebook.name = data["name"]

            if "tags" in data:
                notebook.tags = tag_list_schema.load(data["tags"])

            # At this point "user_id" can only be in "data" if the current
            # request user is an administrator. If the user is not an
            # adminstrator and "user_id" is in "data", we would have returned a
            # 403 response when we checked the permissions.
            if "user_id" in data:
                notebook.user = user_schema.load(data["user_id"])

            message = NOTEBOOK_UPDATED
            code = 200
        else:  # We create a new notebook
            # We validate the data. If any of the Notebook model required
            # fields is missing, a "marshmallow.ValidationError" exception is
            # raised.
            notebook = notebook_schema.load(data)
            result = True

            # Check permissions
            if not jwt["admin"] and jwt["id"] != notebook.user.id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if there is another existing notebook with the same name
            # for the current request user.
            if Notebook.get_by_name(notebook.user.id, tag.name):
                return get_response_data(NOTEBOOK_EXISTS), 400

            message = NOTEBOOK_CREATED
            code = 201

        # Save the notebook
        notebook.save()
        result = notebook.id if result else None

        return get_response_data(message, result), code

    @jwt_required()
    def delete(self, _id: int) -> Response:
        """Handle a Notebook Delete request.

        Delete an existing notebook given its ID. The current request user can
        only call this endpoint if the notebook is one of theirs, unless they
        are an administrator.

        :param _id: Notebook ID.
        :return: Dictionary with the message.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        notebook = Notebook.get_by_id(_id)

        if (
            not jwt["admin"] and (
                not notebook or jwt["id"] != notebook.user.id)
        ):
            return get_response_data(USER_UNAUTHORIZED), 403

        notebook.delete()
        return get_response_data(NOTEBOOK_DELETED), 200
