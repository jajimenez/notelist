"""Notelist "__main__" script."""

import sys

from notelist.app import run
from notelist.config import config


if __name__ == "__main__":
    count = len(sys.argv)

    r = count == 1
    c = count == 2 and sys.argv[1] == "configure"

    if r:
        run()
    elif c:
        config()
    else:
        print("Invalid parameters.")
