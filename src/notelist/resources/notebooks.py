"""Module with the notebook resources."""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt

from notelist.models.notebooks import Notebook
from notelist.schemas.notebooks import NotebookSchema
from notelist.schemas.users import UserSchema
from notelist.schemas.tags import TagSchema
from notelist.resources import Response, OPERATION_NOT_ALLOWED, \
    USER_UNAUTHORIZED, get_response_data


NOTEBOOK_RETRIEVED_1 = "1 notebook retrieved."
NOTEBOOK_RETRIEVED_N = "{} notebooks retrieved."
NOTEBOOK_RETRIEVED = "Notebook retrieved."
NOTEBOOK_CREATED = "Notebook created."
NOTEBOOK_UPDATED = "Notebook updated."
NOTEBOOK_DELETED = "Notebook deleted."
NOTEBOOK_EXISTS = "The user already has a notebook with the same name."

notebook_list_schema = NotebookSchema(many=True)
notebook_schema = NotebookSchema()


class NotebookListResource(Resource):
    """Notebook List resource."""

    @jwt_required()
    def get(self) -> Response:
        """Handle a Notebook List Get request.

        Return all the notebooks of the request user.

        :return: Dictionary with the message and result.
        """
        user_id = get_jwt()["user_id"]
        notebooks = Notebook.get_all(user_id)
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

        Return the request user notebook with the given ID.

        :param _id: Notebook ID.
        :return: Dictionary with the message and result.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        user_id = jwt["user_id"]
        notebook = Notebook.get_by_id(_id)

        if not notebook or user_id != notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(
            NOTEBOOK_RETRIEVED, notebook_schema.dump(notebook)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a Notebook Post request.

        Save a new notebook of the request user given the request data.

        :return: Dictionary with the message and the notebook ID as the result.
        """
        jwt = get_jwt()  # JWT payload data
        user_id = jwt["user_id"]
        data = request.get_json()

        # Check that the request is not for updating an existing notebook
        if "id" in data:
            return get_response_data(OPERATION_NOT_ALLOWED), 403

        notebook = notebook_schema.load(data)
        notebook.user_id = user_id

        # Check that if the notebook already exists
        if Notebook.get_by_name(user_id, notebook.name):
            return get_response_data(NOTEBOOK_EXISTS), 400

        # Save the notebook
        notebook.save()

        return get_response_data(NOTEBOOK_CREATED, notebook.id), 201

    @jwt_required()
    def put(self) -> Response:
        """Handle a Notebook Put request.

        Save a new or existing notebook of the request user with the given
        request data.

        :return: Dictionary with the message and, if the notebook has been
        created, the notebook ID as the result.
        """
        jwt = get_jwt()  # JWT payload data
        user_id = jwt["user_id"]
        data = request.get_json()

        # If there isn't any ID in the request data, we create a new notebook.
        # Otherwise we edit the existing notebook with the given ID.
        edit = "id" in data

        if edit:  # We edit the existing notebook
            notebook = Notebook.get_by_id(data["id"])
            result = False

            # Check permissions
            if not notebook or user_id != notebook.user.id:
                return get_response_data(USER_UNAUTHORIZED), 403

            if "name" in data:
                # Check if the value of the name is new and if there is another
                # existing notebook of the same user with the same name.
                if (
                    data["name"] != notebook.name and
                    Notebook.get_by_name(user_id, data["name"])
                ):
                    return get_response_data(NOTEBOOK_EXISTS), 400

                notebook.name = data["name"]

            message = NOTEBOOK_UPDATED
            code = 200
        else:  # We create a new notebook
            # We validate the data. If any of the Notebook model required
            # fields is missing, a "marshmallow.ValidationError" exception is
            # raised.
            notebook = notebook_schema.load(data)
            notebook.user_id = user_id
            result = True

            # Check if there is another existing notebook with the same name
            # for the request user.
            if Notebook.get_by_name(user_id, notebook.name):
                return get_response_data(NOTEBOOK_EXISTS), 400

            message = NOTEBOOK_CREATED
            code = 201

        # Save the notebook
        notebook.save()
        result = notebook.id if result else None

        return get_response_data(message, result), code

    @jwt_required(fresh=True)
    def delete(self, _id: int) -> Response:
        """Handle a Notebook Delete request.

        Delete an existing notebook of the request user given the notebook ID.

        :param _id: Notebook ID.
        :return: Dictionary with the message.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        user_id = jwt["user_id"]
        notebook = Notebook.get_by_id(_id)

        if not notebook or user_id != notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete the notebook
        notebook.delete()

        return get_response_data(NOTEBOOK_DELETED), 200
