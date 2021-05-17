"""Note resources unit tests."""

import unittest
import time
from typing import Tuple, List, Dict, Optional, Union

import common


TagSet = List[Dict[str, str]]
NoteSet = List[Dict[str, Union[str, bool, List[str]]]]


def _get_tags(notebook_id: str) -> TagSet:
    """Return test tags.

    :param notebook_id: Notebook ID.
    :return: Tuple containing tag names and tag dictionaries.
    """
    return [
        {"notebook_id": notebook_id, "name": "Test Tag 1"},
        {"notebook_id": notebook_id, "name": "Test Tag 2"}]


def _get_notes(notebook_id: str, tags: TagSet) -> NoteSet:
    """Return test notes.

    :param notebook_id: Notebook ID.
    :param tags: Tags.
    :return: List containing note dictionaries.
    """
    return [{
        "notebook_id": notebook_id,
        "active": True,
        "title": "Test Note 1",
        "body": "This is a test note",
        "tags": [t["name"] for t in tags]
    }, {
        "notebook_id": notebook_id,
        "active": True,
        "title": "Test Note 2",
        "body": "This is another test note",
        "tags": [tags[0]["name"]]
    }, {
        "notebook_id": notebook_id,
        "active": False,
        "title": "Test Note 3",
        "body": "Another note",
        "tags": [tags[1]["name"]]
    }, {
        "notebook_id": notebook_id,
        "active": False,
        "title": "Test Note 4",
        "body": "Another note",
        "tags": []
    }]


def _login(client, username: str, password: str) -> Dict[str, str]:
    """Log in.

    :param client: Test API client.
    :param username: Username.
    :param password: Password.
    :return: Headers with the access token.
    """
    data = {"username": username, "password": password}
    r = client.post("/login", json=data)
    access_token = r.json["result"]["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


def _create_notebook(client, headers: Dict[str, str]) -> int:
    """Create a notebook.

    :param client: Test API client.
    :param headers: Headers with the access token.
    :return: Notebook ID.
    """
    n = {"name": "Test Notebook"}
    r = client.post("/notebook", headers=headers, json=n)

    return r.json["result"]


def _create_tags(client, headers: Dict[str, str], tags: TagSet):
    """Create tags.

    :param client: Test API client.
    :param headers: Headers with the access token.
    :param tags: Tags.
    :tags: Tags.
    """
    for t in tags:
        client.post("/tag", headers=headers, json=t)


def _create_notes(
    client, headers: Dict[str, str], notes: NoteSet,
    delay: Optional[int] = None
) -> List[int]:
    """Create notes.

    :param client: Test API client.
    :param headers: Headers with the access token.
    :param notes: Notes.
    :param delay: Delay in seconds between note creations, in order to make the
    notes timestamps different.
    :return: Note IDs.
    """
    note_ids = []

    for n in notes:
        r = client.post("/note", headers=headers, json=n)
        note_ids.append(r.json["result"])

        if delay:
            time.sleep(delay)

    return note_ids


class NoteListTestCase(common.BaseTestCase):
    """Note List resource unit tests."""

    def test_get(self):
        """Test the Get method of the Note List resource.

        This test tries to call the Get method, which shouldn't work.
        """
        r1 = self.client.get("/notes")
        r2 = self.client.get("/notes/1")

        # Check status codes
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

    def test_post(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get the all the notes of the notebook, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all notes
        r = self.client.post(f"/notes/{notebook_id}", headers=headers)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, len(notes))

        for i in range(c):
            self.assertEqual(type(res_notes[i]), dict)
            self.assertEqual(len(res_notes[i]), 7)

            for j in (
                "id", "active", "title", "body", "created_ts",
                "last_modified_ts", "tags"
            ):
                self.assertIn(j, res_notes[i])

            self.assertNotIn("notebook_id", res_notes[i])
            self.assertEqual(res_notes[i]["id"], note_ids[i])

            for j in ("active", "title", "body", "tags"):
                self.assertEqual(res_notes[i][j], notes[i][j])

            self.assertEqual(
                res_notes[i]["created_ts"],
                res_notes[i]["last_modified_ts"])

    def test_post_active(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the active notes of the notebook, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all active notes
        f = {"active": True}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 2)

        for i in range(c):
            self.assertEqual(type(res_notes[i]), dict)
            self.assertEqual(len(res_notes[i]), 7)

            for j in (
                "id", "active", "title", "body", "created_ts",
                "last_modified_ts", "tags"
            ):
                self.assertIn(j, res_notes[i])

            self.assertNotIn("notebook_id", res_notes[i])
            self.assertEqual(res_notes[i]["id"], note_ids[i])

        for i in range(2):
            for j in ("active", "title", "body", "tags"):
                self.assertEqual(res_notes[i][j], notes[i][j])

            self.assertEqual(
                res_notes[i]["created_ts"],
                res_notes[i]["last_modified_ts"])

            self.assertEqual(res_notes[i]["tags"], notes[i]["tags"])

    def test_post_active_tags(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the active notes of the notebook that have any tag of a given
        list of tags, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all active notes with the second tag
        f = {"active": True, "tags": [tag_names[1]]}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 1)

        n = res_notes[0]
        j = 0

        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 7)

        for k in (
            "id", "active", "title", "body", "created_ts", "last_modified_ts",
            "tags"
        ):
            self.assertIn(k, n)

        self.assertNotIn("notebook_id", n)
        self.assertEqual(n["id"], note_ids[j])

        for k in ("active", "title", "body", "tags"):
            self.assertEqual(n[k], notes[j][k])

        self.assertEqual(n["created_ts"], n["last_modified_ts"])
        self.assertEqual(len(n["tags"]), len(notes[j]["tags"]))

        for k in range(len(n["tags"])):
            self.assertEqual(n["tags"][k], notes[j]["tags"][k])

    def test_post_active_tags_no_tags(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the active notes of the notebook that have any tag of a given
        list of tags and all the active notes of the notebook that don't have
        any tag, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all active notes with the second tag
        f = {"active": True, "tags": [tag_names[1]], "no_tags": True}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 1)

        n = res_notes[0]
        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 7)

        j = 0

        for k in (
            "id", "active", "title", "body", "created_ts", "last_modified_ts",
            "tags"
        ):
            self.assertIn(k, n)

        self.assertNotIn("notebook_id", n)
        self.assertEqual(n["id"], note_ids[j])

        for k in ("active", "title", "body", "tags"):
            self.assertEqual(n[k], notes[j][k])

        self.assertEqual(n["created_ts"], n["last_modified_ts"])
        self.assertEqual(len(n["tags"]), len(notes[j]["tags"]))

        for k in range(len(n["tags"])):
            self.assertEqual(n["tags"][k], notes[j]["tags"][k])

    def test_post_inactive(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the inactive notes of the notebook, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all inactive notes
        f = {"active": False}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 2)

        for i in range(c):
            j = i + 2
            self.assertEqual(type(res_notes[i]), dict)
            self.assertEqual(len(res_notes[i]), 7)

            for k in (
                "id", "active", "title", "body", "created_ts",
                "last_modified_ts", "tags"
            ):
                self.assertIn(k, res_notes[i])

            self.assertNotIn("notebook_id", res_notes[i])
            self.assertEqual(res_notes[i]["id"], note_ids[j])

            for k in ("active", "title", "body", "tags"):
                self.assertEqual(res_notes[i][k], notes[j][k])

            self.assertEqual(
                res_notes[i]["created_ts"],
                res_notes[i]["last_modified_ts"])

            self.assertEqual(res_notes[i]["tags"], notes[j]["tags"])

    def test_post_inactive_tags(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the inactive notes of the notebook that have any tag of a given
        list of tags, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all active notes with the second tag
        f = {"active": False, "tags": [tag_names[1]]}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 1)

        n = res_notes[0]
        j = 2

        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 7)

        for k in (
            "id", "active", "title", "body", "created_ts", "last_modified_ts",
            "tags"
        ):
            self.assertIn(k, n)

        self.assertNotIn("notebook_id", n)
        self.assertEqual(n["id"], note_ids[j])

        for k in ("active", "title", "body", "tags"):
            self.assertEqual(n[k], notes[j][k])

        self.assertEqual(n["created_ts"], n["last_modified_ts"])
        self.assertEqual(len(n["tags"]), len(notes[j]["tags"]))

        for k in range(len(n["tags"])):
            self.assertEqual(n["tags"][k], notes[j]["tags"][k])

    def test_post_inactive_tags_no_tags(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the inactive notes of the notebook that have any tag of a given
        list of tags and all the inactive notes of the notebook that don't have
        any tag, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all active notes with the second tag
        f = {"active": False, "tags": [tag_names[1]], "no_tags": True}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 2)

        for i in range(c):
            j = i + 2
            self.assertEqual(type(res_notes[i]), dict)
            self.assertEqual(len(res_notes[i]), 7)

            for k in (
                "id", "active", "title", "body", "created_ts",
                "last_modified_ts", "tags"
            ):
                self.assertIn(k, res_notes[i])

            self.assertNotIn("notebook_id", res_notes[i])
            self.assertEqual(res_notes[i]["id"], note_ids[j])

            for k in ("active", "title", "body", "tags"):
                self.assertEqual(res_notes[i][k], notes[j][k])

            self.assertEqual(
                res_notes[i]["created_ts"],
                res_notes[i]["last_modified_ts"])

            self.assertEqual(res_notes[i]["tags"], notes[j]["tags"])

    def test_post_tags(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook that have any tag of a given list of
        tags, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all notes with the second tag
        f = {"tags": [tag_names[1]]}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 2)

        for i in range(c):
            j = i * 2
            self.assertEqual(type(res_notes[i]), dict)
            self.assertEqual(len(res_notes[i]), 7)

            for k in (
                "id", "active", "title", "body", "created_ts",
                "last_modified_ts", "tags"
            ):
                self.assertIn(k, res_notes[i])

            self.assertNotIn("notebook_id", res_notes[i])
            self.assertEqual(res_notes[i]["id"], note_ids[j])

            for k in ("active", "title", "body", "tags"):
                self.assertEqual(res_notes[i][k], notes[j][k])

            self.assertEqual(
                res_notes[i]["created_ts"],
                res_notes[i]["last_modified_ts"])

            self.assertEqual(res_notes[i]["tags"], notes[j]["tags"])

    def test_post_tags_no_tags(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook that have any tag of a given list of
        tags and all the notes of the notebook that don't have any tag, which
        should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all notes with the second tag
        f = {"tags": [tag_names[1]], "no_tags": True}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 3)
        j1 = {0: 0, 1: 2, 2: 3}

        for i in range(c):
            j2 = j1[i]
            self.assertEqual(type(res_notes[i]), dict)
            self.assertEqual(len(res_notes[i]), 7)

            for k in (
                "id", "active", "title", "body", "created_ts",
                "last_modified_ts", "tags"
            ):
                self.assertIn(k, res_notes[i])

            self.assertNotIn("notebook_id", res_notes[i])
            self.assertEqual(res_notes[i]["id"], note_ids[j2])

            for k in ("active", "title", "body", "tags"):
                self.assertEqual(res_notes[i][k], notes[j2][k])

            self.assertEqual(
                res_notes[i]["created_ts"],
                res_notes[i]["last_modified_ts"])

            self.assertEqual(res_notes[i]["tags"], notes[j2]["tags"])

    def test_post_no_tags_1(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook that don't have any tag, which should
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all notes without tags
        f = {"tags": [], "no_tags": True}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, 1)

        n = res_notes[0]
        j = 3

        self.assertEqual(type(n), dict)
        self.assertEqual(len(n), 7)

        for k in (
            "id", "active", "title", "body", "created_ts", "last_modified_ts",
            "tags"
        ):
            self.assertIn(k, n)

        self.assertNotIn("notebook_id", n)
        self.assertEqual(n["id"], note_ids[j])

        for k in ("active", "title", "body", "tags"):
            self.assertEqual(n[k], notes[j][k])

        self.assertEqual(n["created_ts"], n["last_modified_ts"])
        self.assertEqual(len(n["tags"]), 0)

    def test_post_no_tags_2(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook filtering by tags with an empty tag
        list and without selecting the notes that have no tags (which should be
        no notes), which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get all notes without tags
        f = {"tags": []}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 0)

        # Get all notes without tags
        f = {"tags": [], "no_tags": False}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        self.assertEqual(len(res_notes), 0)

    def test_post_last_mod(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook sorted by their Last Modified
        timestamp, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes, 1)

        # Edit the second note
        n = {"title": "New title"}
        r = self.client.put(f"/note/{note_ids[1]}", headers=headers, json=n)

        # Get notes sorted by Last Modified timetamp (ascending)
        f = {"last_mod": True}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, len(notes))
        expected_ids = [note_ids[0]] + note_ids[2:] + [note_ids[1]]

        for i in range(c):
            self.assertEqual(res_notes[i]["id"], expected_ids[i])

        # Get notes sorted by Last Modified timetamp (descending)
        f = {"last_mod": True, "asc": False}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)
        res_notes = r.json["result"]

        # Check list
        self.assertEqual(type(res_notes), list)
        c = len(res_notes)
        self.assertEqual(c, len(notes))

        for i in range(c):
            self.assertEqual(res_notes[i]["id"], expected_ids[-(i + 1)])

    def test_post_missing_access_token(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and some notes and then
        tries to get all the notes of the notebook without providing the access
        token, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get notes
        r = self.client.post(f"/notes/{notebook_id}")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and notes and then tries to
        get all the notes of the notebook providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get notes providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_invalid_invalid_field(self):
        """Test the Post method of the Note List resource.

        This test creates a notebook with some tags and some notes and then
        tries to get all the notes of the notebook providing an invalid field,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        tag_names = [t["name"] for t in tags]
        _create_tags(self.client, headers, tags)

        # Create notes
        notes = _get_notes(notebook_id, tags)
        note_ids = _create_notes(self.client, headers, notes)

        # Get notes providing an invalid field ("invalid_field")
        f = {"active": True, "invalid_field": 1}
        r = self.client.post(f"/notes/{notebook_id}", headers=headers, json=f)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put(self):
        """Test the Put method of the Note List resource.

        This test tries to call the Put method, which shouldn't work.
        """
        r1 = self.client.put("/notes")
        r2 = self.client.put("/notes/1")

        # Check status codes
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)

    def test_delete(self):
        """Test the Delete method of the Note List resource.

        This test tries to call the Delete method, which shouldn't work.
        """
        r1 = self.client.delete("/notes")
        r2 = self.client.delete("/notes/1")

        # Check status codes
        self.assertEqual(r1.status_code, 404)
        self.assertEqual(r2.status_code, 405)


class NoteTestCase(common.BaseTestCase):
    """Note resource unit tests."""

    def test_get(self):
        """Test the Get method of the Note resource.

        This test creates a notebook with a note and then tries to get the
        note, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        _create_tags(self.client, headers, tags)

        # Create note
        n = _get_notes(notebook_id, tags)[0]
        note_id = _create_notes(self.client, headers, [n])[0]

        # Get note
        r = self.client.get(f"/note/{note_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Check result
        self.assertIn("result", r.json)
        note = r.json["result"]
        self.assertEqual(type(note), dict)
        self.assertEqual(len(note), 7)

        for i in (
            "id", "active", "title", "body", "created_ts", "last_modified_ts",
            "tags"
        ):
            self.assertIn(i, note)

        self.assertNotIn("notebook_id", note)
        self.assertEqual(note["id"], note_id)

        for i in ("active", "title", "body", "tags"):
            self.assertEqual(note[i], n[i])

        self.assertEqual(note["created_ts"], note["last_modified_ts"])

    def test_get_missing_access_token(self):
        """Test the Get method of the Note resource.

        This test tries to get the data of some note without providing the
        access token, which shouldn't work.
        """
        # Get the note with ID 1 (which doesn't exist) without providing the
        # access token.
        r = self.client.get("/note/1")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_get_invalid_access_token(self):
        """Test the Get method of the Note resource.

        This test tries to get the data of some note providing an invalid
        access token, which shouldn't work.
        """
        # Get the note with ID 1 (which doesn't exist) providing an invalid
        # access token ("1234").
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.get("/note/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_get_unauthorized_user(self):
        """Test the Get method of the Note resource.

        This test tries to get a note of a user from another user, which
        shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create tags
        tags = _get_tags(notebook_id)
        _create_tags(self.client, headers, tags)

        # Create note
        n = _get_notes(notebook_id, tags)[0]
        note_id = _create_notes(self.client, headers, [n])[0]

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Get note
        r = self.client.get(f"/note/{note_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_get_note_not_found(self):
        """Test the Get method of the Note resource.

        This test tries to get a note that doesn't exist, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Get the note with ID 1 (which doesn't exist)
        r = self.client.get("/note/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post(self):
        """Test the Post method of the Note resource.

        This test tries to create a note, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.post("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        note_id = r.json["result"]
        self.assertEqual(type(note_id), int)

        # Check notebook tags
        r = self.client.get(f"/tags/{notebook_id}", headers=headers)
        tags = r.json["result"]
        tag_names = [t["name"] for t in tags]
        self.assertEqual(tag_names, n["tags"])

    def test_post_missing_access_token(self):
        """Test the Post method of the Note resource.

        This test tries to create a note without providing the access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.post("/note", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_post_invalid_access_token(self):
        """Test the Post method of the Note resource.

        This test tries to create a note providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create a note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.post("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_post_missing_fields(self):
        """Test the Post method of the Note resource.

        This test tries to create a note with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note (without data)
        r = self.client.post("/note", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create note (without the notebook ID)
        r = self.client.post("/note", headers=headers, json=dict())

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_invalid_fields(self):
        """Test the Post method of the Note resource.

        This test tries to create a note providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create a note with an invalid field ("invalid_field")
        n = {"notebook_id": notebook_id, "invalid_field": 1}
        r = self.client.post("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_post_notebook_user_unauthorized(self):
        """Test the Post method of the Note resource.

        This test tries to create a note for a notebook that doesn't belong to
        the request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create note
        n = {"notebook_id": notebook_id}
        r = self.client.post("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_post_notebook_not_found(self):
        """Test the Post method of the Note resource.

        This test tries to create a note for a notebook that doesn't exist,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create a note for the notebook with ID 1 (which doesn't exist)
        n = {"notebook_id": 1}
        r = self.client.post("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_new(self):
        """Test the Put method of the Note resource.

        This test tries to create a note, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 201)

        # Check result
        self.assertIn("result", r.json)
        note_id = r.json["result"]
        self.assertEqual(type(note_id), int)

        # Check notebook tags
        r = self.client.get(f"/tags/{notebook_id}", headers=headers)
        tags = r.json["result"]
        tag_names = [t["name"] for t in tags]
        self.assertEqual(tag_names, n["tags"])

    def test_put_edit(self):
        """Test the Put method of the Note resource.

        This test tries to edit one of the notes of one of the request user's
        notebooks, which should work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Edit note
        new_tag = {
            "active": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]}
        r = self.client.put(f"/note/{note_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get note
        r = self.client.get(f"/note/{note_id}", headers=headers)
        note = r.json["result"]

        # Check note
        for i in (
            "id", "active", "title", "body", "created_ts", "last_modified_ts",
            "tags"
        ):
            self.assertIn(i, note)

        self.assertNotIn("notebook_id", note)
        self.assertEqual(note["id"], note_id)

        for i in ("active", "title", "body", "tags"):
            self.assertEqual(note[i], new_tag[i])

        self.assertEqual(note["created_ts"], note["last_modified_ts"])

    def test_put_new_missing_access_token(self):
        """Test the Put method of the Note resource.

        This test tries to create a note without providing the access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", json=n)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_edit_missing_access_token(self):
        """Test the Put method of the Note resource.

        This test tries to edit one of the notes of one of the request user's
        notebooks without providing the access token, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Edit note
        new_tag = {
            "active": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]}
        r = self.client.put(f"/note/{note_id}", json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_put_new_invalid_access_token(self):
        """Test the Put method of the Note resource.

        This test tries to create a note providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_edit_invalid_access_token(self):
        """Test the Put method of the Note resource.

        This test tries to edit a note providing an invalid access token, which
        shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Edit note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        new_tag = {
            "active": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]}
        r = self.client.put(f"/note/{note_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_put_new_missing_fields(self):
        """Test the Put method of the Note resource.

        This test tries to create a note with some mandatory field missing,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note without data
        r = self.client.put("/note", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 400)

        # Create note without the notebook ID
        n = {
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_notebook(self):
        """Test the Put method of the Note resource.

        This test tries to edit a note specifying its notebook, which shouldn't
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Edit note
        new_tag = {
            "notebook_id": notebook_id,
            "active": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"]}
        r = self.client.put(f"/note/{note_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_invalid_fields(self):
        """Test the Put method of the Note resource.

        This test tries to create a note providing some invalid/unexpected
        field, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note with an invalid field ("invalid_field")
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"],
            "invalid_field": 1}
        r = self.client.put("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_edit_invalid_fields(self):
        """Test the Put method of the Note resource.

        This test tries to edit a note providing some invalid/unexpected field,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Edit note with an invalid field ("invalid_field")
        new_tag = {
            "notebook_id": notebook_id,
            "active": False,
            "title": "New Test Note",
            "body": "This is a new test note",
            "tags": ["New Test Tag 1", "New Test Tag 2"],
            "invalid_field": 1}
        r = self.client.put(f"/note/{note_id}", headers=headers, json=new_tag)

        # Check status code
        self.assertEqual(r.status_code, 400)

    def test_put_new_notebook_user_unauthorized(self):
        """Test the Put method of the Note resource.

        This test tries to create a note for a notebook that doesn't belong to
        the request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_new_notebook_not_found(self):
        """Test the Put method of the Note resource.

        This test tries to create a note for a notebook that doesn't exist,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create note for the notebook with ID 1 (which doesn't exist)
        n = {
            "notebook_id": 1,
            "active": True,
            "title": "Test Note 1",
            "body": "This is a test note",
            "tags": ["Test Tag 1", "Test Tag 2", "Test Tag 3"]}
        r = self.client.put("/note", headers=headers, json=n)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_put_edit_user_unauthorized(self):
        """Test the Put method of the Note resource.

        This test tries to edit a note of a notebook that doesn't belong to the
        request user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note 1"}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Edit note
        new_note = {"title": "Test Note 2"}
        r = self.client.put(f"/tag/{note_id}", headers=headers, json=new_note)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete(self):
        """Test the Delete method of the Note resource.

        This test creates a note and then tries to delete it, which should
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note"}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Get notebook note list
        r = self.client.post(f"/notes/{notebook_id}", headers=headers)
        notes = r.json["result"]

        # Check list
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["id"], note_id)
        self.assertEqual(notes[0]["active"], n["active"])
        self.assertEqual(notes[0]["title"], n["title"])

        # Delete note
        r = self.client.delete(f"/note/{note_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 200)

        # Get notebook note list
        r = self.client.post(f"/notes/{notebook_id}", headers=headers)
        notes = r.json["result"]

        # Check list
        self.assertEqual(len(notes), 0)

    def test_delete_missing_access_token(self):
        """Test the Delete method of the Note resource.

        This test tries to delete an existing note without providing the access
        token, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note"}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Delete note
        r = self.client.delete(f"/note/{note_id}")

        # Check status code
        self.assertEqual(r.status_code, 401)

    def test_delete_invalid_access_token(self):
        """Test the Delete method of the Note resource.

        This test tries to delete a note providing an invalid access token,
        which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note"}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Delete note providing an invalid access token ("1234")
        headers = {"Authorization": "Bearer 1234"}
        r = self.client.delete(f"/note/{note_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 422)

    def test_delete_unauthorized_user(self):
        """Test the Delete method of the Note resource.

        This test tries to delete a note of a user different than the request
        user, which shouldn't work.
        """
        # Log in
        headers = _login(
            self.client, self.admin["username"], self.admin["password"])

        # Create notebook
        notebook_id = _create_notebook(self.client, headers)

        # Create note
        n = {
            "notebook_id": notebook_id,
            "active": True,
            "title": "Test Note"}
        r = self.client.put("/note", headers=headers, json=n)
        note_id = r.json["result"]

        # Log in as another user
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Delete note
        r = self.client.delete(f"/note/{note_id}", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)

    def test_delete_note_not_found(self):
        """Test the Delete method of the Note resource.

        This test tries to delete a note that doesn't exist, which shouldn't
        work.
        """
        # Log in
        headers = _login(
            self.client, self.reg1["username"], self.reg1["password"])

        # Delete the note with ID 1 (which doesn't exist)
        r = self.client.delete("/note/1", headers=headers)

        # Check status code
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":
    unittest.main()
