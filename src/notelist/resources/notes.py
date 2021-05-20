"""Module with the note resources."""

from typing import Optional

from datetime import datetime
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt

from notelist.apis import notes_api
from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.models.notes import Note
from notelist.schemas.notes import NoteSchema
from notelist.resources import Response, VALIDATION_ERROR, USER_UNAUTHORIZED, \
    get_response_data


NOTE_RETRIEVED_1 = "1 note retrieved."
NOTE_RETRIEVED_N = "{} notes retrieved."
NOTE_RETRIEVED = "Note retrieved."
NOTE_CREATED = "Note created."
NOTE_UPDATED = "Note updated."
NOTE_DELETED = "Note deleted."

note_list_schema = NoteSchema(many=True)
note_schema = NoteSchema()


@notes_api.route("/notes/<int:notebook_id>")
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
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Get the notebook
        notebook = Notebook.get_by_id(notebook_id)

        # Check if the notebook exists and the permissions
        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Request data
        fields = ["active", "tags", "no_tags", "last_mod", "asc"]
        data = request.get_json() or {}

        # Check if the request data contains any invalid field
        inv_fields = ", ".join([
            i for i in data if i not in fields])

        if inv_fields:
            return get_response_data(VALIDATION_ERROR.format(inv_fields)), 400

        # State filter (include active notes or not active notes)
        f = fields[0]

        if f in data:
            active = data[f]

            if type(active) != bool:
                return get_response_data(VALIDATION_ERROR.format(f)), 400
        else:
            active = None

        # Tag filter (include notes that has any of these tags)
        f = fields[1]

        if f in data:
            tags = data[f]

            if (
                type(tags) != list or
                any(map(lambda t: type(t) != str or not t.strip(), tags))
            ):
                return get_response_data(VALIDATION_ERROR.format(f)), 400

            tags = [t.strip() for t in tags]
        else:
            tags = None

        # Notes with No Tags filter (include notes with no tags). This filter
        # is only applicable if a tag filter has been provided, i.e. "tags" is
        # not None).
        f = fields[2]

        if f in data:
            no_tags = data[f]

            if tags is None or type(no_tags) != bool:
                return get_response_data(VALIDATION_ERROR.format(f)), 400
        else:
            no_tags = None

        # Order by Last Modified timestamp
        f = fields[3]

        if f in data:
            last_mod = data[f]

            if last_mod is None or type(last_mod) != bool:
                return get_response_data(VALIDATION_ERROR.format(f)), 400
        else:
            last_mod = False

        # Ascending order
        f = fields[4]

        if f in data:
            asc = data[f]

            if asc is None or type(asc) != bool:
                return get_response_data(VALIDATION_ERROR.format(f)), 400
        else:
            asc = True

        notes = Note.get_by_filter(
            notebook_id, active, tags, no_tags, last_mod, asc)

        c = len(notes)
        m = NOTE_RETRIEVED_1 if c == 1 else NOTE_RETRIEVED_N.format(c)

        return get_response_data(m, note_list_schema.dump(notes)), 200


@notes_api.route("/note", "/note/<int:note_id>")
class NoteResource(Resource):
    """Note resource."""

    def _get_current_ts(self) -> int:
        """Return current timestamp rounded.

        :return: 10-digit integer timestamp.
        """
        return round(datetime.now().timestamp())

    def _select_tag(self, notebook_id: int, name: str) -> Tag:
        """Returns a copy of a given request data tag if the tag doesn't exist
        in the notebook or the existing tag.

        :notebook_id: Notebook ID.
        :param name: Request data tag name.
        :return: Copy of `t` or the existing tag.
        """
        tag = Tag.get_by_name(notebook_id, name)
        return tag if tag else Tag(notebook_id=notebook_id, name=name)

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

        # Check if the note exists and the permissions
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
        data = request.get_json() or {}

        # Current timestamp
        now = self._get_current_ts()

        # We validate the request data. If any of the Note model required
        # fields is missing, a "marshmallow.ValidationError" exception is
        # raised.
        note = note_schema.load(data)

        if note.title:
            note.title = note.title.strip()

        # Check if the note's notebook user is the same as the request user
        notebook = Notebook.get_by_id(note.notebook_id)

        if not notebook or uid != notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Set Created and Last modified timestamps
        note.created_ts = now
        note.last_modified_ts = now

        # For each request data tag, check if the tag already exists in the
        # notebook and if so, replace the request data tag by the existing tag.
        # This way, the request tags that already exist won't be created again,
        # as they will have their ID value defined (not None).
        note.tags = list(map(
            lambda t: self._select_tag(note.notebook_id, t.name), note.tags))

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
        data = request.get_json() or {}

        # Current timestamp
        now = self._get_current_ts()

        # If "note_id" is None, we create a new note. Otherwise we edit the
        # existing note with the given ID.
        new = note_id is None

        if new:
            # We validate the request data. If any of the Note model required
            # fields is missing, or any provided field is invalid, a
            # "marshmallow.ValidationError" exception is raised.
            note = note_schema.load(data)

            if note.title:
                note.title = note.title.strip()

            # Get note's notebook
            notebook = Notebook.get_by_id(note.notebook_id)

            # Check if the notebook exists and the permissions (the request
            # user must be the same as the notebook's user).
            if not notebook or uid != notebook.user_id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Set Created timestamp
            note.created_ts = now

            # For each request data tag, check if the tag already exists in the
            # notebook and if so, replace the request data tag by the existing
            # tag. This way, the request tags that already exist won't be
            # created again, as they will have their ID value defined (not
            # None). As "note" is a new note, the tags will be saved when
            # calling "note.save".
            note.tags = list(map(
                lambda t: self._select_tag(note.notebook_id, t.name),
                note.tags))

            message = NOTE_CREATED
            code = 201
        else:
            # Get existing note
            note = Note.get(note_id)

            # Check if the note exists and the permissions
            if not note or uid != note.notebook.user_id:
                return get_response_data(USER_UNAUTHORIZED), 403

            # Make a copy of the request data
            data = data.copy()

            # Check if a new value for the "notebook_id" field is provided,
            # which is not allowed.
            if "notebook_id" in data:
                return get_response_data(
                    VALIDATION_ERROR.format("notebook_id")), 400
            else:
                data["notebook_id"] = note.notebook_id

            # Check if new values for the state, the title, the body or the
            # tags are provided.
            if "active" not in data:
                data["active"] = note.active

            if "title" not in data:
                data["title"] = note.title

            if "body" not in data:
                data["body"] = note.body

            if "tags" not in data:
                data["tags"] = [t.name for t in note.tags]

            # We validate the request data. If any provided field is invalid,
            # a "marshmallow.ValidationError" exception is raised.
            new_note = note_schema.load(data)

            if new_note.title:
                new_note.title = new_note.title.strip()

            # For each tag, check if the tag already exists in the notebook and
            # if so, replace the tag object by the existing tag object (which
            # contains its ID). This way, the tags that already exist won't be
            # created again as they will have their ID value defined (not
            # None).
            tags = list(map(
                lambda t: self._select_tag(new_note.notebook_id, t.name),
                new_note.tags))

            # Update note object. Note: we can't run "note.tags =
            # new_note.tags", as it would duplicate the note in the database
            # (that's why "tags" is a different list object).
            note.active = new_note.active
            note.title = new_note.title
            note.body = new_note.body
            note.tags = tags

            message = NOTE_UPDATED
            code = 200

        # Set Last Modified timestamp
        note.last_modified_ts = now

        # Save note
        note.save()
        result = note.id if new else None

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
        note = Note.get(note_id)

        # Check if the note exists and the permissions (the request user must
        # be the same as the note's notebook user).
        if not note or uid != note.notebook.user_id:
            return get_response_data(USER_UNAUTHORIZED), 403

        # Delete note
        note.delete()

        return get_response_data(NOTE_DELETED), 200
