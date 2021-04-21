"""Module with the tag resources."""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.schemas.tags import TagSchema
from notelist.resources import Response, USER_UNAUTHORIZED, get_response_data


TAG_RETRIEVED_1 = "1 tag retrieved."
TAG_RETRIEVED_N = "{} tags retrieved."
TAG_RETRIEVED = "Tag retrieved."
TAG_CREATED = "Tag created."
TAG_UPDATED = "Tag updated."
TAG_DELETED = "Tag deleted."
TAG_EXISTS = "A tag with the same name already exists in the notebook."

tag_list_schema = TagSchema(many=True)
tag_schema = TagSchema()


class TagListResource(Resource):
    """Tag resource.

    This resource manages the operations of all the tags of a notebook.
    """

    @jwt_required()
    def get(self, _id: int) -> Response:
        """Handle a Tag List Get request.

        Return all the tags of a notebook given the notebook ID. The request
        user can only call this endpoint for one of their notebooks.

        :param _id: Notebook ID.
        :return: Dictionary with the message and result.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        notebook = Notebook.get_by_id(_id)

        if not notebook or jwt["user_id"] != notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        tags = Tag.get_all(notebook.id)
        count = len(tags)

        if count == 1:
            message = TAG_RETRIEVED_1
        else:
            message = TAG_RETRIEVED_N.format(count)

        return get_response_data(message, tag_list_schema.dump(tags)), 200


class TagResource(Resource):
    """Tag resource.

    This resource manages the operations of a single notebook tag.
    """

    @jwt_required()
    def get(self, _id: int) -> Response:
        """Handle a Tag Get request.

        Return the tag with the given ID. The request user can only call this
        endpoint for a tag of any of their own notebooks.

        :param _id: Tag ID.
        :return: Dictionary with the message and result.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        tag = Tag.get_by_id(_id)

        if not tag or jwt["user_id"] != tag.notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(TAG_RETRIEVED, tag_schema.dump(tag)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a Tag Post request.

        Save a new tag with the given data. The request user can only call this
        endpoint if the tag notebook is one of theirs.

        :return: Dictionary with the message and the tag ID as the result.
        """
        # Check that the request is not for updating an existing tag
        data = request.get_json()

        if "id" in data:
            return get_response_data(OPERATION_NOT_ALLOWED), 403

        # Check permissions
        jwt = get_jwt()  # JWT payload data
        tag = tag_schema.load(data)
        notebook = Notebook.get_by_id(tag.notebook_id)

        if not notebook or jwt["user_id"] != notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Check if a tag with the same name already exists in the notebook
        if Tag.get_by_name(notebook.id, tag.name):
            return get_response_data(TAG_EXISTS), 400

        # Save the tag
        tag.save()

        return get_response_data(TAG_CREATED, tag.id), 201

    @jwt_required()
    def put(self) -> Response:
        """Handle a Tag Put request.

        Save a new or existing tag with the given data. The request user can
        only call this endpoint if the tag notebook is one of theirs.

        :return: Dictionary with the message and, if the tag has been created,
        the tag ID as the result.
        """
        jwt = get_jwt()  # JWT payload data
        user_id = jwt["user_id"]
        data = request.get_json()

        # If there isn't any ID in the request data, we create a new tag.
        # Otherwise we edit the existing tag with the given ID.
        edit = "id" in data

        if edit:  # We edit the existing tag
            tag = Tag.get_by_id(data["id"])
            result = False

            # Check permissions
            if not tag or user_id != tag.notebook.user.id:
                return get_response_data(USER_UNAUTHORIZED), 403

            if "notebook_id" in data:
                # Check if the value of the notebook ID is new and if the user
                # of the new notebook is the request user.
                if data["notebook_id"] != tag.notebook.id:
                    notebook = Notebook.get_by_id(data["notebook_id"])

                    if not notebook or user_id != notebook.user.id:
                        return get_response_data(USER_UNAUTHORIZED), 403

            if "name" in data:
                # Check if the value of the name is new and if there is an
                # existing tag with the same name in the notebook.
                if "notebook_id" in data:
                    notebook_id = data["notebook_id"] 
                else:
                    notebook_id = tag.notebook.id

                if (
                    data["name"] != tag.name and
                    Tag.get_by_name(notebook_id, data["name"])
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
            result = True

            # Check permissions
            if jwt["user_id"] != tag.notebook.user.id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if there is any existing tag with the same name in the same
            # notebook.
            if Tag.get_by_name(tag.notebook_id, tag.name):
                return get_response_data(TAG_EXISTS), 400

            message = TAG_CREATED
            code = 201

        # Save the tag
        tag.save()
        result = tag.id if result else None

        return get_response_data(message, result), code

    @jwt_required()
    def delete(self, _id: int) -> Response:
        """Handle a Tag Delete request.

        Delete an existing tag given its ID. The request user can only call
        this endpoint if the tag notebook is one of theirs.

        :param _id: Tag ID.
        :return: Dictionary with the message.
        """
        # Check permissions
        jwt = get_jwt()  # JWT payload data
        tag = Tag.get_by_id(_id)

        if not tag or jwt["user_id"] != tag.notebook.user.id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete the tag
        tag.delete()

        return get_response_data(TAG_DELETED), 200
