"""Notelist - Core - Models."""

from django.db.models import (
    Model,
    CharField,
    TextField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    CASCADE,
)

from django.contrib.auth.models import User


def get_preview(text: str) -> str:
    """Get the first 20 characters of a text.

    :param text: Original text.
    :rtype: str
    :return: First 20 characters of the original text.
    :rtype: str
    """
    m = 20
    return text[: m - 3] + "..." if len(text) > m else text


class Notebook(Model):
    """Notebook model."""

    user = ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=CASCADE,
        related_name="notebooks",
    )

    name = CharField(null=False, blank=False, max_length=200)

    created = DateTimeField(
        null=False, blank=False, auto_now_add=True, editable=False
    )

    updated = DateTimeField(null=False, blank=False, auto_now=True)

    class Meta:
        """Notebook model options."""

        verbose_name = "notebook"
        verbose_name_plural = "notebooks"

    def __str__(self) -> str:
        """Get the string representation of the instance."""
        return get_preview(self.name)


class Tag(Model):
    """Tag model."""

    notebook = ForeignKey(
        Notebook,
        null=False,
        blank=False,
        on_delete=CASCADE,
        related_name="tags",
    )

    name = CharField(null=False, blank=False, max_length=200)
    color = CharField(null=True, blank=True, max_length=7, default=None)

    created = DateTimeField(
        null=False, blank=False, auto_now_add=True, editable=False
    )

    updated = DateTimeField(null=False, blank=False, auto_now=True)

    class Meta:
        """Tag model options."""

        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self) -> str:
        """Get the string representation of the instance."""
        return get_preview(self.name)


class Note(Model):
    """Note model."""

    notebook = ForeignKey(
        Notebook,
        null=False,
        blank=False,
        on_delete=CASCADE,
        related_name="notes",
    )

    title = CharField(null=True, blank=True, max_length=200)
    body = TextField(null=True, blank=True)
    tags = ManyToManyField(Tag, blank=True, related_name="notes")
    active = BooleanField(null=False, blank=False, default=True)

    created = DateTimeField(
        null=False, blank=False, auto_now_add=True, editable=False
    )

    updated = DateTimeField(null=False, blank=False, auto_now=True)

    class Meta:
        """Note model options."""

        verbose_name = "note"
        verbose_name_plural = "notes"

    def __str__(self) -> str:
        """Get the string representation of the instance."""
        return get_preview(self.title) if self.title else ""
