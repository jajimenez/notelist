"""Module with the tag resources."""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.schemas.tags import TagSchema
from notelist.resources import Response, USER_UNAUTHORIZED, get_response_data


TAG_RETRIEVED = "Tag retrieved."
TAG_CREATED = "Tag created."
TAG_UPDATED = "Tag updated."
TAG_DELETED = "Tag deleted."
TAG_NOT_FOUND = "Tag not found."
TAG_EXISTS = "Another tag with the same name already exists in the notebook."

tag_schema = TagSchema()


class TagResource(Resource):
    """Tag resource."""

    @jwt_required()
    def get(self, _id: int) -> Response:
        """Handle a Tag Get request.

        Return the tag with the given ID. The current request user can only
        call this endpoint for the tags of their own notebooks, unless they are
        an administrator.

        :param _id: Tag ID.
        :return: Dictionary with the message and result.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        tag = Tag.get_by_id(_id)

        if not jwt["admin"] and (not tag or jwt["id"] != tag.notebook.user.id):
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(TAG_RETRIEVED, tag_schema.dump(tag)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a Tag Post request.

        Save a new tag with the given data. The current request user can only
        call this endpoint if the tag notebook is one of theirs, unless they
        are an administrator.

        :return: Dictionary with the message.
        """
        # Check that the request is not for updating an existing tag
        data = request.get_json()

        if "id" in data:
            return get_response_data(OPERATION_NOT_ALLOWED), 403

        # Check permissions
        jwt = get_jwt()  # JWT payload data
        tag = tag_schema.load(data)

        if not jwt["admin"] and jwt["id"] != tag.notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        tag.save()
        return get_response_data(TAG_CREATED), 201

    @jwt_required()
    def put(self) -> Response:
        """Handle a Tag Put request.

        Save a new or existing tag with the given data. The current request
        user can only call this endpoint if the tag notebook is one of theirs,
        unless they are an administrator.

        :return: Dictionary with the message.
        """
        jwt = get_jwt()  # JWT payload data
        data = request.get_json()

        # If there isn't any ID in the request data, we create a new tag.
        # Otherwise we update the tag with the given ID.
        if "id" in data:  # We update the tag
            tag = Tag.get_by_id(data["id"])

            if jwt["admin"] and not tag:
                return get_response_data(TAG_NOT_FOUND), 404

            # Check permissions
            if (
                not jwt["admin"] and
                (not tag or jwt["id"] != tag.notebook.user.id)
            ):
                return get_response_data(USER_UNAUTHORIZED), 403

            if "name" in data:
                # Check if the value of the name is new and if there is another
                # existing tag with the same name in the same notebook.
                if (
                    data["name"] != tag.name and
                    Tag.get_by_name(data["notebook_id"], data["name"])
                ):
                    return get_response_data(TAG_EXISTS), 400

                tag.name = data["name"]

            if "color" in data:
                tag.color = data["color"]

            message = TAG_UPDATED
            code = 200
        else:  # We create a new tag
            # We validate the data. If any of the Tag model required fields is
            # missing, a "marshmallow.ValidationError" exception is raised.
            tag = tag_schema.load(data)

            # Check permissions
            if not jwt["admin"] and jwt["id"] != tag.notebook.user.id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if there is another existing tag with the same name in the
            # same notebook.
            if Tag.get_by_name(tag.notebook_id, tag.name):
                return get_response_data(TAG_EXISTS), 400

            message = TAG_CREATED
            code = 201

        tag.save()
        return get_response_data(message), code

    @jwt_required()
    def delete(self, _id: int) -> Response:
        """Handle a Tag Delete request.

        Delete an existing tag given its ID. The current request user can only
        call this endpoint if the tag notebook is one of theirs, unless they
        are an administrator.

        :param _id: Tag ID.
        :return: Dictionary with the message.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        tag = Tag.get_by_id(_id)

        if not jwt["admin"] and (not tag or jwt["id"] != tag.notebook.user.id):
            return get_response_data(USER_UNAUTHORIZED), 403

        tag.delete()
        return get_response_data(TAG_DELETED), 200
