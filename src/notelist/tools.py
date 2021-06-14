"""Tools module."""

from uuid import uuid4
from datetime import datetime
import hashlib as hl


def generate_uuid() -> str:
    """Generate a random UUID.

    :return: Random UUID. E.g. "2a7602ec-3198-48a7-82fb-3c39afaa0844".
    """
    return str(uuid4())


def get_current_ts() -> int:
    """Get current timestamp.

    :return: 10-digit current timestamp in seconds. E.g. 1623706743.
    """
    return int(datetime.now().timestamp())


def get_hash(text: str) -> str:
    """Return the hash of a text.

    :param text: Original text.
    :return: Text hash.
    """
    s = hl.sha256()
    s.update(bytes(text, encoding="utf-8"))

    return s.hexdigest()
