"""Main module."""

import sys

from notelist.app import run
from notelist.config import config


RUN_ARG = "--rp"
CONF_ARG = "configure"
INVALID_ARGS = "Invalid arguments."


def main():
    """Run the application."""
    count = len(sys.argv)

    if count == 1:
        # Run application
        run()
    elif count == 3 and sys.argv[1] == RUN_ARG:
        # Run application with an initial password for the "root" administrator
        # user.
        run(sys.argv[2])
    elif count == 2 and sys.argv[1] == CONF_ARG:
        # Run the configuration user interface
        config()
    else:
        print(INVALID_ARGS)
