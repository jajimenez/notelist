"""Main module."""

import sys

from notelist.app import run
from notelist.config import config


CONF_ARG = "configure"
INVALID_ARGS = "Invalid arguments."


def main():
    """Run the application."""
    count = len(sys.argv)

    if count == 1:
        run()
    elif count == 2 and sys.argv[1] == CONF_ARG:
        config()
    else:
        print(INVALID_ARGS)
