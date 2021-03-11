"""Tools module."""

import hashlib as hl


def get_border_title(title: str) -> str:
    """Return a string with borders given a title.

    :param title: Title.
    :return: Title with borders.
    """
    border = f'+{"-" * (len(title) + 2)}+'
    return f"{border}\n| {title} |\n{border}"


def get_hash(text: str) -> str:
    """Return the hash of a text.

    :param text: Original text.
    :return: Text hash.
    """
    s = hl.sha256()
    s.update(bytes(text, encoding="utf-8"))

    return s.hexdigest()
