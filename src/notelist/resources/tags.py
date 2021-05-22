"""Module with the tag resources."""

from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from notelist.apis import tags_api
from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.schemas.tags import TagSchema
from notelist.resources import (
    Response, VALIDATION_ERROR, OPERATION_NOT_ALLOWED,
    USER_UNAUTHORIZED, get_response_data, get_response_codes)


TAG_RETRIEVED_1 = "1 tag retrieved."
TAG_RETRIEVED_N = "{} tags retrieved."
TAG_RETRIEVED = "Tag retrieved."
TAG_CREATED = "Tag created."
TAG_UPDATED = "Tag updated."
TAG_DELETED = "Tag deleted."
TAG_EXISTS = "A tag with the same name already exists in the notebook."

tag_list_schema = TagSchema(many=True)
tag_schema = TagSchema()


@tags_api.route("/tags/<int:notebook_id>")
@tags_api.doc(params={"notebook_id": "Notebook ID (integer)"})
class TagListResource(Resource):
    """Tag list resource."""

    @jwt_required()
    @tags_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def get(self, notebook_id: int) -> Response:
        """Get all the tags of a notebook.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message and the tags data.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook exists and the permissions
        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Get notebook tags
        tags = sorted(notebook.tags, key=lambda t: t.id)
        c = len(tags)
        m = TAG_RETRIEVED_1 if c == 1 else TAG_RETRIEVED_N.format(c)

        return get_response_data(m, tag_list_schema.dump(tags)), 200


@tags_api.route("/tag")
class NewTagResource(Resource):
    """New tags resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = tags_api.model(
        "NewTag", {
            "notebook_id": fields.Integer(required=True),
            "name": fields.String(required=True),
            "color": fields.String(default=None, example="#00ff00")})

    def _create_tag(self) -> Response:
        """Create a new tag.

        :return: Dictionary with the message and the tag ID.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json() or {}

        # We validate the request data. If any of the Tag model required fields
        # is missing, a "marshmallow.ValidationError" exception is raised.
        tag = tag_schema.load(data)
        tag.name = tag.name.strip()

        if not tag.name:
            return get_response_data(VALIDATION_ERROR.format("name")), 400

        # Check if the notebook exists and the permissions (the request user
        # must be the same as the notebook's user).
        notebook = Notebook.get_by_id(tag.notebook_id)

        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Check if the notebook already has the tag (based on the tag name)
        if Tag.get_by_name(notebook.id, tag.name):
            return get_response_data(TAG_EXISTS), 400

        # Save tag
        tag.save()

        return get_response_data(TAG_CREATED, tag.id), 201

    @jwt_required()
    @tags_api.expect(req_fields)
    @tags_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 403, 422))
    def post(self) -> Response:
        """Create a new tag.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the tag ID.
        """
        return self._create_tag()

    @jwt_required()
    @tags_api.expect(req_fields)
    @tags_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 403, 422))
    def put(self) -> Response:
        """Create a new tag.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the tag ID.
        """
        return self._create_tag()


@tags_api.route("/tag/<int:tag_id>")
@tags_api.doc(params={"tag_id": "Tag ID (integer)"})
class ExistingTagResource(Resource):
    """Existing tags resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = tags_api.model(
        "ExistingTag", {"name": fields.String, "color": fields.String})

    @jwt_required()
    @tags_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def get(self, tag_id: int) -> Response:
        """Get an existing tag's data.

        The user can call this operation only for their own notebooks' tags.
        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param tag_id: Tag ID.
        :return: Dictionary with the message and the tag data.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get tag
        tag = Tag.get_by_id(tag_id)

        # Check if the tag exists and the permissions
        if not tag or uid != tag.notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(TAG_RETRIEVED, tag_schema.dump(tag)), 200

    @jwt_required()
    @tags_api.expect(req_fields)
    @tags_api.doc(
        security="apikey",
        responses=get_response_codes(200, 400, 401, 403, 422))
    def put(self, tag_id: int) -> Response:
        """Edit an existing tag.

        The user can call this operation only for their own notebooks' tags and
        the notebook ID of the tag cannot be changed. This operation requires
        the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param tag_id: Tag ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json() or {}

        # Get existing tag
        tag = Tag.get_by_id(tag_id)

        # Check if the tag exists and the permissions
        if not tag or uid != tag.notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Make a copy of the request data
        data = data.copy()

        # Check if a new value for the "notebook_id" field is provided,
        # which is not allowed.
        if "notebook_id" in data:
            return get_response_data(
                VALIDATION_ERROR.format("notebook_id")), 400
        else:
            data["notebook_id"] = tag.notebook_id

        # Check if a new value for the name is provided and if the notebook
        # has already a tag with this name.
        if "name" in data:
            if type(data["name"]) != str or not data["name"].strip():
                return get_response_data(
                    VALIDATION_ERROR.format("name")), 400

            data["name"] = data["name"].strip()

            if (
                data["name"] != tag.name and
                Tag.get_by_name(tag.notebook_id, data["name"])
            ):
                return get_response_data(TAG_EXISTS), 400
        else:
            data["name"] = tag.name

        # Check if a new value for the color is provided
        if "color" not in data:
            data["color"] = tag.color

        # We validate the request data. If any provided field is invalid,
        # a "marshmallow.ValidationError" exception is raised.
        new_tag = tag_schema.load(data)

        # Update tag object
        tag.name = new_tag.name
        tag.color = new_tag.color

        message = TAG_UPDATED
        code = 200

        # Save tag
        tag.save()

        return get_response_data(TAG_UPDATED), 200

    @jwt_required()
    @tags_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def delete(self, tag_id: int) -> Response:
        """Delete an existing tag.

        The user can call this operation only for their own notebooks' tags.
        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param tag_id: Tag ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get tag
        tag = Tag.get_by_id(tag_id)

        # Check if the tag exists and the permissions (the request user must be
        # the same as the tag's notebook user).
        if not tag or uid != tag.notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete tag
        tag.delete()

        return get_response_data(TAG_DELETED), 200
