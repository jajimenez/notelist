"""Module with the note resources."""

from datetime import datetime
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt

from notelist.apis import notes_api
from notelist.models.notebooks import Notebook
from notelist.models.tags import Tag
from notelist.models.notes import Note
from notelist.schemas.notes import NoteSchema
from notelist.resources import (
    Response, VALIDATION_ERROR, USER_UNAUTHORIZED, get_response_codes,
    get_response_data)


NOTE_RETRIEVED_1 = "1 note retrieved."
NOTE_RETRIEVED_N = "{} notes retrieved."
NOTE_RETRIEVED = "Note retrieved."
NOTE_CREATED = "Note created."
NOTE_UPDATED = "Note updated."
NOTE_DELETED = "Note deleted."

note_list_schema = NoteSchema(many=True)
note_schema = NoteSchema()


@notes_api.route("/notes/<int:notebook_id>")
@notes_api.doc(params={"notebook_id": "Notebook ID (integer)"})
class NoteListResource(Resource):
    """Note list resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    fields = notes_api.model(
        "Filter", {
            "active": fields.Boolean,
            "tags": fields.List(fields.String, default=[]),
            "no_tags": fields.Boolean,
            "last_mod": fields.Boolean,
            "asc": fields.Boolean})

    @jwt_required()
    @notes_api.doc(
        security="apikey",
        responses=get_response_codes(200, 400, 401, 403, 422))
    def post(self, notebook_id: int) -> Response:
        """Get all the notes of a notebook that match a filter.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param notebook_id: Notebook ID.
        :return: Dictionary with the message and the notes data.
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


@notes_api.route("/note")
class NewNoteResource(Resource):
    """New notes resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = notes_api.model(
        "NewNote", {
            "notebook_id": fields.Integer(required=True),
            "active": fields.Boolean(default=True),
            "title": fields.String(default=None),
            "body": fields.String(default=None),
            "tags": fields.List(fields.String, default=[])})

    def _get_current_ts(self) -> int:
        """Return current timestamp rounded.

        :return: 10-digit integer timestamp.
        """
        return round(datetime.now().timestamp())

    def _select_tag(self, notebook_id: int, name: str) -> Tag:
        """Return a copy of a given request data tag if the tag doesn't exist
        in the notebook or the existing tag.

        :notebook_id: Notebook ID.
        :param name: Request data tag name.
        :return: Copy of `t` or the existing tag.
        """
        tag = Tag.get_by_name(notebook_id, name)
        return tag if tag else Tag(notebook_id=notebook_id, name=name)

    def _create_note(self) -> Response:
        """Create a new note.

        :return: Dictionary with the message and the note ID.
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
    @notes_api.expect(req_fields)
    @notes_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 403, 422))
    def post(self) -> Response:
        """Create a new note.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the tag ID.
        """
        return self._create_note()

    @jwt_required()
    @notes_api.expect(req_fields)
    @notes_api.doc(
        security="apikey",
        responses=get_response_codes(201, 400, 401, 403, 422))
    def put(self) -> Response:
        """Create a new note.

        The user can call this operation only for their own notebooks. This
        operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :return: Dictionary with the message and the tag ID.
        """
        return self._create_note()


@notes_api.route("/note/<int:note_id>")
@notes_api.doc(params={"note_id": "Note ID (integer)"})
class ExistingNoteResource(Resource):
    """Existing notes resource."""

    # This model is for the HTML documentation that is automatically generated
    # for the root route ("/"). It shouldn't be confused with the database
    # models of the "notelist.models" module or the schemas of the "notelist.
    # schemas" module.
    req_fields = notes_api.model(
        "ExistingNote", {
            "active": fields.Boolean,
            "title": fields.String,
            "body": fields.String,
            "tags": fields.List(fields.String)})

    def _get_current_ts(self) -> int:
        """Return current timestamp rounded.

        :return: 10-digit integer timestamp.
        """
        return round(datetime.now().timestamp())

    def _select_tag(self, notebook_id: int, name: str) -> Tag:
        """Return a copy of a given request data tag if the tag doesn't exist
        in the notebook or the existing tag.

        :notebook_id: Notebook ID.
        :param name: Request data tag name.
        :return: Copy of `t` or the existing tag.
        """
        tag = Tag.get_by_name(notebook_id, name)
        return tag if tag else Tag(notebook_id=notebook_id, name=name)

    @jwt_required()
    @notes_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def get(self, note_id: int) -> Response:
        """Get an existing note's data.

        The user can call this operation only for their own notebooks' notes.
        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param note_id: Note ID.
        :return: Dictionary with the message and the note data.
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
    @notes_api.expect(req_fields)
    @notes_api.doc(
        security="apikey",
        responses=get_response_codes(200, 400, 401, 403, 422))
    def put(self, note_id: int) -> Response:
        """Edit an existing note.

        The user can call this operation only for their own notebooks' notes
        and the notebook ID of the note cannot be changed. This operation
        requires the following header with an access token:
            "Authorization" = "Bearer access_token"

        :param note_id: Note ID.
        :return: Dictionary with the message.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Request data
        data = request.get_json() or {}

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

        # Update Last Modified timestamp
        note.last_modified_ts = self._get_current_ts()

        # Save note
        note.save()

        return get_response_data(NOTE_UPDATED), 200

    @jwt_required()
    @notes_api.doc(
        security="apikey",
        responses=get_response_codes(200, 401, 403, 422))
    def delete(self, note_id: int) -> Response:
        """Delete an existing note.

        The user can call this operation only for their own notebooks' notes.
        This operation requires the following header with an access token:
            "Authorization" = "Bearer access_token"

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
