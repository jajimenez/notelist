"""Module with the notebook resources."""

from typing import Optional

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt

from notelist.models.notebooks import Notebook
from notelist.schemas.notebooks import NotebookSchema
from notelist.resources import \
    Response, VALIDATION_ERROR, USER_UNAUTHORIZED, get_response_data


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
        # Get all the notebooks of the request user
        uid = get_jwt()["user_id"]  # JWT payload data
        notebooks = Notebook.get_all(uid)

        c = len(notebooks)
        m = NOTEBOOK_RETRIEVED_1 if c == 1 else NOTEBOOK_RETRIEVED_N.format(c)

        return get_response_data(m, notebook_list_schema.dump(notebooks)), 200


class NotebookResource(Resource):
    """Notebook resource."""

    @jwt_required()
    def get(self, notebook_id: int) -> Response:
        """Handle a Notebook Get request.

        Return the request user notebook with the given ID.

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message and result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get the notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook doesn't exist and the permissions
        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(
            NOTEBOOK_RETRIEVED, notebook_schema.dump(notebook)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a Notebook Post request.

        Save a new notebook of the request user given the request data.

        :return: Dictionary with the message and the notebook ID as the result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json()

        # We validate the request data. If any of the Notebook model required
        # fields is missing, a "marshmallow.ValidationError" exception is
        # raised.
        notebook = notebook_schema.load(data)

        # Check if the request user already has the notebook (based on the
        # notebook name).
        if Notebook.get_by_name(uid, notebook.name):
            return get_response_data(NOTEBOOK_EXISTS), 400

        # Save the notebook
        notebook.user_id = uid
        notebook.save()

        return get_response_data(NOTEBOOK_CREATED, notebook.id), 201

    @jwt_required()
    def put(self, notebook_id: Optional[int] = None) -> Response:
        """Handle a Notebook Put request.

        Save a new or existing notebook of the request user with the given
        request data. The "user_id" field of an existing notebook is not
        allowed to be modified.

        :param _id: ID of the notebook to update or None to create a new
        notebook.
        :return: Dictionary with the message and, if the notebook has been
        created, the notebook ID as the result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json()

        # If "notebook_id" is None, we create a new notebook. Otherwise we edit
        # the existing notebook with the given ID.
        new_notebook = notebook_id is None

        if new_notebook:
            # We validate the request data. If any of the Notebook model
            # required fields is missing, a "marshmallow.ValidationError"
            # exception is raised.
            notebook = notebook_schema.load(data)

            # Check if the notebook already exists (based on the name) for the
            # request user.
            if Notebook.get_by_name(uid, notebook.name):
                return get_response_data(NOTEBOOK_EXISTS), 400

            notebook.user_id = uid
            message = NOTEBOOK_CREATED
            code = 201
        else:
            # Get existing notebook
            notebook = Notebook.get_by_id(notebook_id)

            # Check if the notebook doesn't exist (based on the name) for the
            # request user and check the permissions (the request user must be
            # the same as the notebook user).
            if not notebook or uid != notebook.user_id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if the request data contains any invalid field (i.e. any
            # field that doesn't exist in the notebook model schema).
            fields = ", ".join([
                i for i in data if i not in notebook_schema.load_fields])

            if fields:
                return get_response_data(VALIDATION_ERROR.format(fields)), 400

            # Check if a new name is provided and if the request user has
            # already a notebook with this name.
            if "name" in data:
                if (
                    data["name"] != notebook.name and
                    Notebook.get_by_name(uid, data["name"])
                ):
                    return get_response_data(NOTEBOOK_EXISTS), 400

                notebook.name = data["name"]

            message = NOTEBOOK_UPDATED
            code = 200

        # Save the notebook
        notebook.save()
        result = notebook.id if new_notebook else None

        return get_response_data(message, result), code

    @jwt_required(fresh=True)
    def delete(self, notebook_id: int) -> Response:
        """Handle a Notebook Delete request.

        Delete an existing notebook of the request user given the notebook ID.

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook doesn't exist and the permissions (the request
        # user can only delete their own notebooks).
        if not notebook or uid != notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete notebook
        notebook.delete()

        return get_response_data(NOTEBOOK_DELETED), 200
