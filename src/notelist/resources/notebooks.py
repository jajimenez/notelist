"""Module with the notebook resources."""

from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt

from notelist.apis import notebooks_api
from notelist.models.notebooks import Notebook
from notelist.schemas.notebooks import NotebookSchema
from notelist.resources import (
    Response, VALIDATION_ERROR, USER_UNAUTHORIZED, get_response_codes,
    get_response_data)


NOTEBOOK_RETRIEVED_1 = "1 notebook retrieved."
NOTEBOOK_RETRIEVED_N = "{} notebooks retrieved."
NOTEBOOK_RETRIEVED = "Notebook retrieved."
NOTEBOOK_CREATED = "Notebook created."
NOTEBOOK_UPDATED = "Notebook updated."
NOTEBOOK_DELETED = "Notebook deleted."
NOTEBOOK_EXISTS = "The user already has a notebook with the same name."

notebook_list_schema = NotebookSchema(many=True)
notebook_schema = NotebookSchema()


@notebooks_api.route("/notebooks")
class NotebookListResource(Resource):
    """Notebook list resource."""

    @jwt_required()
    @notebooks_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 422))
    def get(self) -> Response:
        """Get all the notebooks of the request user.

        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the users data.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get all the notebooks of the request user
        notebooks = Notebook.get_all(uid)

        c = len(notebooks)
        m = NOTEBOOK_RETRIEVED_1 if c == 1 else NOTEBOOK_RETRIEVED_N.format(c)

        return get_response_data(m, notebook_list_schema.dump(notebooks)), 200


@notebooks_api.route("/notebook")
class NewNotebookResource(Resource):
    """New notebooks resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = notebooks_api.model(
        "NewNotebook", {"name": fields.String(required=True)})

    def _create_notebook(self) -> Response:
        """Create a new notebook.

        :return: Dictionary with the message and the notebook ID.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json() or {}

        # We validate the request data. If any of the Notebook model required
        # fields is missing, a "marshmallow.ValidationError" exception is
        # raised.
        notebook = notebook_schema.load(data)
        notebook.name = notebook.name.strip()

        if not notebook.name:
            return get_response_data(VALIDATION_ERROR.format("name")), 400

        # Check if the request user already has the notebook (based on the
        # notebook name).
        if Notebook.get_by_name(uid, notebook.name):
            return get_response_data(NOTEBOOK_EXISTS), 400

        # Save notebook
        notebook.user_id = uid
        notebook.save()

        return get_response_data(NOTEBOOK_CREATED, notebook.id), 201

    @jwt_required()
    @notebooks_api.expect(req_fields)
    @notebooks_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 422))
    def post(self) -> Response:
        """Create a new notebook.

        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the notebook ID.
        """
        return self._create_notebook()

    @jwt_required()
    @notebooks_api.expect(req_fields)
    @notebooks_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 422))
    def put(self) -> Response:
        """Create a new notebook.

        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the notebook ID.
        """
        return self._create_notebook()


@notebooks_api.route("/notebook/<int:notebook_id>")
@notebooks_api.doc(params={"notebook_id": "Notebook ID (integer)"})
class ExistingNotebookResource(Resource):
    """Existing notebooks resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = notebooks_api.model(
        "ExistingNotebook", {"name": fields.String})

    @jwt_required()
    @notebooks_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def get(self, notebook_id: int) -> Response:
        """Get an existing notebook's data.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message and the notebook data.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get the notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook exists and the permissions
        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(
            NOTEBOOK_RETRIEVED, notebook_schema.dump(notebook)), 200

    @jwt_required()
    @notebooks_api.expect(req_fields)
    @notebooks_api.doc(
        security="apikey",
        responses=get_response_codes(200, 400, 401, 403, 422))
    def put(self, notebook_id: int) -> Response:
        """Edit an existing notebook.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json() or {}

        # Get existing notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook exists (based on its name) for the request
        # user and check the permissions (the request user must be the same
        # as the notebook user).
        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Make a copy of the request data
        data = data.copy()

        # Check if a new name is provided and if the request user has
        # already a notebook with this name.
        if "name" in data:
            if type(data["name"]) != str or not data["name"].strip():
                return get_response_data(
                    VALIDATION_ERROR.format("name")), 400

            data["name"] = data["name"].strip()

            if (
                data["name"] != notebook.name and
                Notebook.get_by_name(uid, data["name"])
            ):
                return get_response_data(NOTEBOOK_EXISTS), 400
        else:
            data["name"] = notebook.name

        # We validate the request data. If any provided field is invalid,
        # a "marshmallow.ValidationError" exception is raised.
        new_notebook = notebook_schema.load(data)

        # Update notebook object
        notebook.name = new_notebook.name

        # Save the notebook
        notebook.save()

        return get_response_data(NOTEBOOK_UPDATED), 200

    @jwt_required(fresh=True)
    @notebooks_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def delete(self, notebook_id: int) -> Response:
        """Delete an existing notebook.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with a fresh access token:
            "Authorization" = "Bearer fresh_access_token"

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook exists and the permissions (the request user
        # can only delete their own notebooks).
        if not notebook or uid != notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete notebook
        notebook.delete()

        return get_response_data(NOTEBOOK_DELETED), 200
