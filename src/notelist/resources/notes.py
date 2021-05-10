"""Module with the note resources."""

from typing import Optional

from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt

from notelist.models.notebooks import Notebook
from notelist.models.notes import Note
from notelist.schemas.notes import NoteSchema
from notelist.resources import Response, MISSING_DATA, VALIDATION_ERROR, \
    USER_UNAUTHORIZED, get_response_data


NOTE_RETRIEVED_1 = "1 note retrieved."
NOTE_RETRIEVED_N = "{} notes retrieved."
NOTE_RETRIEVED = "Note retrieved."
NOTE_CREATED = "Note created."
NOTE_UPDATED = "Note updated."
NOTE_DELETED = "Note deleted."

note_list_schema = NoteSchema(many=True)
note_schema = NoteSchema()


class NoteListResource(Resource):
    """Note List resource."""

    @jwt_required()
    def post(self, notebook_id: int) -> Response:
        """Handle a Note List Get request.

        Return all the notes of one of the request user's notebooks given some
        filters in the request data.

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message and result.
        """
        # Request data fields
        act = "active"
        tag = "tags"
        nta = "no_tags"
        sea = "search"

        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get the notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook doesn't exist and the permissions
        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Request data
        data = request.get_json() or dict()

        # State filter (include active notes or not active notes)
        if act in data:
            active = data[act]

            if type(active) != bool:
                return get_response_data(VALIDATION_ERROR.format(act)), 400
        else:
            active = None

        # Tags filter (include notes that has any of these tags)
        if tag in data:
            tags = data[tag]

            if (
                type(tags) != list or
                any(map(lambda x: type(x) != int or not x, tags))
            ):
                return get_response_data(VALIDATION_ERROR.format(tag)), 400
        else:
            tags = None

        # Notes with No Tags filter (include notes with no tags). This filter
        # is only applicable if a tag filter has been provided, i.e. "tags" is
        # not None).
        if nta in data:
            no_tags = data[nta]

            if tags is None or type(no_tags) != bool:
                return get_response_data(VALIDATION_ERROR.format(nta)), 400
        else:
            no_tags = None

        notes = Note.get_by_filter(notebook_id, active, tags, no_tags)
        c = len(notes)
        m = NOTE_RETRIEVED_1 if c == 1 else NOTE_RETRIEVED_N.format(c)

        return get_response_data(m, note_list_schema.dump(notes)), 200


class NoteResource(Resource):
    """Note resource."""

    def _get_current_ts(self) -> int:
        """Return current timestamp rounded.

        :return: 10-digit integer timestamp.
        """
        return round(datetime.now().timestamp())

    @jwt_required()
    def get(self, note_id: int) -> Response:
        """Handle a Note Get request.

        Return the request user's note with the given ID.

        :param note_id: Note ID.
        :return: Dictionary with the message and the note data as the result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get the note
        note = Note.get(note_id)

        # Check if the note doesn't exist and the permissions
        if not note or uid != note.notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        return get_response_data(NOTE_RETRIEVED, note_schema.dump(note)), 200

    @jwt_required()
    def post(self) -> Response:
        """Handle a Note Post request.

        Save a new note with the given request data. The request user can only
        call this endpoint if the note's notebook is one of theirs.

        :return: Dictionary with the message and the note ID as the result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json()

        if not data:
            return get_response_data(MISSING_DATA), 400

        # Current timestamp
        now = self._get_current_ts()

        # We validate the request data. If any of the Note model required
        # fields is missing, a "marshmallow.ValidationError" exception is
        # raised.
        note = tag_schema.load(data)

        # Check if the note's notebook user is the same as the request user
        notebook = Notebook.get_by_id(note.notebook_id)

        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Set creation and last modification timestamps
        note.creation_ts = now
        note.last_modification_ts = now

        # Save note
        note.save()

        return get_response_data(NOTE_CREATED, note.id), 201

    @jwt_required()
    def put(self, note_id: Optional[int] = None) -> Response:
        """Handle a Note Put request.

        Save a new or existing note with the given request data. The request
        user can only call this endpoint if the note's notebook is one of
        theirs. The "notebook_id" field must be specified when creating a new
        note but is not allowed to be updated for an existing note.

        :param note_id: ID of the note to update or None to create a new note.
        :return: Dictionary with the message and, if the note has been created,
        the note ID as the result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json()

        if not data:
            return get_response_data(MISSING_DATA), 400

        # Current timestamp
        now = self._get_current_ts()

        # If "note_id" is None, we create a new note. Otherwise we edit the
        # existing note with the given ID.
        new_note = note_id is None

        if new_note:
            # We validate the request data. If any of the Note model required
            # fields is missing, a "marshmallow.ValidationError" exception is
            # raised.
            note = note_schema.load(data)

            # Get note's notebook
            notebook = Notebook.get_by_id(note.notebook_id)

            # Check if the notebook doesn't exist and the permissions (the
            # request user must be the same as the notebook's user).
            if not notebook or uid != notebook.user_id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Set creation timestamp
            note.creation_ts = now

            message = NOTE_CREATED
            code = 201
        else:
            # Get existing note
            note = Note.get(note_id)

            # Check if the note doesn't exist and the permissions
            if not note or uid != note.notebook.user_id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Check if the request data contains any invalid field (i.e. any
            # field that doesn't exist in the Note model schema).
            fields = ", ".join([
                i for i in data if i not in note_schema.load_fields])

            if fields:
                return get_response_data(VALIDATION_ERROR.format(fields)), 400

            # Check if a new value for the "notebook_id" field is provided,
            # which is not allowed.
            if "notebook_id" in data:
                return get_response_data(
                    VALIDATION_ERROR.format("notebook_id")), 400

            # Check if a new value for the state is provided
            if "active" in data:
                note.active = data["active"]

            # Check if a new value for the title is provided
            if "title" in data:
                note.title = data["title"]

            # Check if a new value for the body is provided
            if "body" in data:
                note.body = data["body"]

            message = NOTE_UPDATED
            code = 200

        # Set last modification timestamp
        note.last_modification_ts = now

        # Save note
        note.save()
        result = note.id if new_note else None

        return get_response_data(message, result), code

    @jwt_required()
    def delete(self, note_id: int) -> Response:
        """Handle a Note Delete request.

        Delete an existing note of one of the request user's notebooks given
        the note's ID.

        :param note_id: Note ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get note
        note = Tag.get_by_id(note_id)

        # Check if the note doesn't exist and the permissions (the request user
        # must be the same as the note's notebook user).
        if not note or uid != note.notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete note
        note.delete()

        return get_response_data(NOTE_DELETED), 200
