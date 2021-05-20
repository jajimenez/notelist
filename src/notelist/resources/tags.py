"""Module with the tag resources."""

from typing import Optional

from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from notelist.apis import tags_api
from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.schemas.tags import TagSchema
from notelist.resources import Response, VALIDATION_ERROR, \
    OPERATION_NOT_ALLOWED, USER_UNAUTHORIZED, get_response_data


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
class TagListResource(Resource):
    """Tag resource.

    This resource manages the operations of all the tags of a notebook.
    """

    @jwt_required()
    def get(self, notebook_id: int) -> Response:
        """Handle a Tag List Get request.

        Return all the tags of a notebook given the notebook ID. The request
        user can only call this endpoint for one of their notebooks.

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message and result.
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


@tags_api.route("/tag", "/tag/<int:tag_id>")
class TagResource(Resource):
    """Tag resource.

    This resource manages the operations of a single notebook tag.
    """

    @jwt_required()
    def get(self, tag_id: int) -> Response:
        """Handle a Tag Get request.

        Return the tag with the given ID. The request user can only call this
        endpoint for a tag of any of their own notebooks.

        :param tag_id: Tag ID.
        :return: Dictionary with the message and result.
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
    def post(self) -> Response:
        """Handle a Tag Post request.

        Save a new tag with the given request data. The request user can only
        call this endpoint if the tag's notebook is one of theirs.

        :return: Dictionary with the message and the tag ID as the result.
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
    def put(self, tag_id: Optional[int] = None) -> Response:
        """Handle a Tag Put request.

        Save a new or existing tag with the given request data. The request
        user can only call this endpoint if the tag's notebook is one of
        theirs. The "notebook_id" field must be specified when creating a new
        tag but is not allowed to be updated for an existing tag.

        :param tag_id: ID of the tag to update or None to create a new tag.
        :return: Dictionary with the message and, if the tag has been created,
        the tag ID as the result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json() or {}

        # If "tag_id" is None, we create a new tag. Otherwise we edit the
        # existing tag with the given ID.
        new = tag_id is None

        if new:
            # We validate the request data. If any of the Tag model required
            # fields is missing, a "marshmallow.ValidationError" exception is
            # raised.
            tag = tag_schema.load(data)
            tag.name = tag.name.strip()

            if not tag.name:
                return get_response_data(VALIDATION_ERROR.format("name")), 400

            # Get tag's notebook
            notebook = Notebook.get_by_id(tag.notebook_id)

            # Check if the notebook exists and the permissions (the request
            # user must be the same as the notebook's user).
            if not notebook or uid != notebook.user_id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if there is any existing tag with the same name in the
            # notebook.
            if Tag.get_by_name(notebook.id, tag.name):
                return get_response_data(TAG_EXISTS), 400

            message = TAG_CREATED
            code = 201
        else:
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
        result = tag.id if new else None

        return get_response_data(message, result), code

    @jwt_required()
    def delete(self, tag_id: int) -> Response:
        """Handle a Tag Delete request.

        Delete an existing tag of one of the request user's notebooks given the
        tag's ID.

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
