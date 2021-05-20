"""Module with the search resources."""

from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt

from notelist.apis import search_api
from notelist.resources import Response, VALIDATION_ERROR, get_response_data
from notelist.models.notebooks import Notebook
from notelist.schemas.notebooks import NotebookSchema
from notelist.schemas.tags import TagSchema
from notelist.schemas.notes import NoteSchema


ITEM_RETRIEVED_1 = "1 item retrieved."
ITEM_RETRIEVED_N = "{} items retrieved."

notebook_list_schema = NotebookSchema(many=True)
tag_list_schema = TagSchema(many=True)
note_list_schema = NoteSchema(many=True)


@search_api.route("/search/<search>")
class SearchResource(Resource):
    """Search resource."""

    @jwt_required()
    def get(self, search: str) -> Response:
        """Handle a Search Get request.

        Return all the notebooks, tags and notes that match a search string.

        :return: Dictionary with the message and result.
        """
        # JWT payload data
        uid = get_jwt()["user_id"]

        # Check search string
        search = search.strip().lower()

        if len(search) < 2:
            return get_response_data(VALIDATION_ERROR.format("search")), 400

        # Notebooks
        notebooks = Notebook.get_all(uid)
        res_notebooks = [n for n in notebooks if search in n.name.lower()]

        # Notes and tags
        res_tags = []
        res_notes = []

        for nb in notebooks:
            res_tags += [
                t for t in nb.tags if (
                    search in t.name.lower() or
                    (t.color and search in t.color.lower()))]

            res_notes += [
                n for n in nb.notes if (
                    (n.title and search in n.title.lower()) or
                    (n.body and search in n.body.lower()) or
                    (any(map(lambda t: search in t.name.lower(), n.tags))))]

        result = {
            "notebooks": notebook_list_schema.dump(res_notebooks),
            "tags": tag_list_schema.dump(res_tags),
            "notes": note_list_schema.dump(res_notes)}

        c = len(res_notebooks) + len(res_notes) + len(res_tags)
        m = ITEM_RETRIEVED_1 if c == 1 else ITEM_RETRIEVED_N.format(c)

        return get_response_data(m, result), 200
