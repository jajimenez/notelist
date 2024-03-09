"""Notelist - Core - Tests."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Notebook, Tag, Note


class ModelTests(TestCase):
    """Model tests."""

    def setUp(self):
        """Set up the tests."""
        # Create user
        self.user_model = get_user_model()

        self.user_username = "user"
        self.user_password = "password"

        self.user = self.user_model.objects.create_user(
            username=self.user_username, password=self.user_password
        )

        # Create notebook
        self.notebook_name = "Notebook"
        self.notebook = self.user.notebooks.create(name=self.notebook_name)

        # Create tag
        self.tag_name = "Tag"
        self.tag_color = "#000000"

        self.tag = self.notebook.tags.create(
            name=self.tag_name, color=self.tag_color
        )

        # Create note
        self.note_title = "Note"
        self.note_body = "Test note."

        self.note = self.notebook.notes.create(
            title=self.note_title, body=self.note_body
        )

        self.note.tags.add(self.tag)

    def test_create_user(self):
        """Test creating a user."""
        # Check user attributes
        self.assertIsNotNone(self.user.id)
        self.assertEqual(self.user.username, self.user_username)
        self.assertTrue(self.user.check_password(self.user_password))

    def test_delete_user(self):
        """Test deleting a user."""
        # Check that the user and the notebook exist
        user_id = self.user.id
        notebook_id = self.notebook.id

        self.assertTrue(self.user_model.objects.filter(id=user_id).exists())
        self.assertTrue(Notebook.objects.filter(id=notebook_id).exists())

        # Delete user
        self.user.delete()

        # Check that the user and the notebook don't exist
        self.assertFalse(self.user_model.objects.filter(id=user_id).exists())
        self.assertFalse(Notebook.objects.filter(id=notebook_id).exists())

    def test_create_notebook(self):
        """Test creating a notebook."""
        # Check notebook attributes
        self.assertIsNotNone(self.notebook.id)
        self.assertEqual(self.notebook.user, self.user)
        self.assertEqual(self.notebook.user, self.user)
        self.assertEqual(self.notebook.name, self.notebook_name)

    def test_delete_notebook(self):
        """Test deleting a notebook."""
        # Check that the tag and the note exist
        tag_id = self.tag.id
        note_id = self.note.id

        self.assertTrue(Tag.objects.filter(id=tag_id).exists())
        self.assertTrue(self.note.tags.filter(id=note_id).exists())

        # Delete notebook
        self.notebook.delete()

        # Check that the tag and the note don't exist
        self.assertFalse(Tag.objects.filter(id=tag_id).exists())
        self.assertFalse(self.note.tags.filter(id=note_id).exists())

    def test_create_tag(self):
        """Test creating a tag."""
        # Check tag attributes
        self.assertIsNotNone(self.tag.id)
        self.assertEqual(self.tag.notebook, self.notebook)
        self.assertEqual(self.tag.name, self.tag_name)
        self.assertEqual(self.tag.color, self.tag_color)

    def test_update_tag(self):
        """Test updating a tag."""
        # Check tag attributes
        self.assertEqual(self.tag.name, self.tag_name)
        self.assertEqual(self.tag.color, self.tag_color)

        # Check notebook and note tags attributes
        tag_id = self.tag.id
        notebook_tag = self.notebook.tags.get(id=tag_id)

        self.assertEqual(notebook_tag.name, self.tag_name)
        self.assertEqual(notebook_tag.color, self.tag_color)

        note_tag = self.note.tags.get(id=tag_id)

        self.assertEqual(note_tag.name, self.tag_name)
        self.assertEqual(note_tag.color, self.tag_color)

        # Update tag
        new_name = "New Tag"
        new_color = "#ffffff"

        self.tag.name = new_name
        self.tag.color = new_color
        self.tag.save()

        # Check tag attributes
        tag = Tag.objects.get(id=tag_id)

        self.assertEqual(tag.name, new_name)
        self.assertEqual(tag.color, new_color)

        # Check notebook and note tags attributes
        notebook_tag = self.notebook.tags.get(id=tag_id)

        self.assertEqual(notebook_tag.name, new_name)
        self.assertEqual(notebook_tag.color, new_color)

        note_tag = self.note.tags.get(id=tag_id)

        self.assertEqual(note_tag.name, new_name)
        self.assertEqual(note_tag.color, new_color)

    def test_delete_tag(self):
        """Test deleting a tag."""
        # Check that the tag exists and it's associated with the notebook and
        # the note.
        tag_id = self.tag.id

        self.assertTrue(Tag.objects.filter(id=tag_id).exists())
        self.assertTrue(self.notebook.tags.filter(id=tag_id).exists())
        self.assertTrue(self.note.tags.filter(id=tag_id).exists())

        # Delete tag
        self.tag.delete()

        # Check that the tag doesn't exist and it's not associated with the
        # notebook or the note.
        self.assertFalse(Tag.objects.filter(id=tag_id).exists())
        self.assertFalse(self.notebook.tags.filter(id=tag_id).exists())
        self.assertFalse(self.note.tags.filter(id=tag_id).exists())

    def test_create_note(self):
        """Test creating a note."""
        # Check note
        self.assertIsNotNone(self.note.id)
        self.assertEqual(self.note.notebook, self.notebook)
        self.assertEqual(self.note.title, self.note_title)
        self.assertEqual(self.note.body, self.note_body)
        self.assertEqual(self.note.tags.count(), 1)
        self.assertEqual(self.note.tags.first(), self.tag)
        self.assertTrue(self.note.active)
        self.assertIsNotNone(self.note.created)
        self.assertIsNotNone(self.note.updated)

    def test_delete_note(self):
        """Test deleting a note."""
        # Check that the note and the tag exist
        note_id = self.note.id
        tag_id = self.tag.id

        self.assertTrue(Note.objects.filter(id=note_id).exists())
        self.assertTrue(Tag.objects.filter(id=tag_id).exists())

        # Delete note
        self.note.delete()

        # Check that the note doesn't exist but the tag does
        self.assertFalse(Note.objects.filter(id=note_id).exists())
        self.assertTrue(Tag.objects.filter(id=tag_id).exists())
