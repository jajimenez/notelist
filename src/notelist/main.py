"""Main module."""

import sys

from notelist.app import run
from notelist.config import config


CONF_ARG = "configure"
INVALID_ARGS = "Invalid arguments."


def main():
    """Run the application."""
    count = len(sys.argv)

    r = count == 1
    c = count == 2 and sys.argv[1] == CONF_ARG

    if r:
        run()
    elif c:
        config()
    else:
        print(INVALID_ARGS)
