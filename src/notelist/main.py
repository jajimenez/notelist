"""Main module."""

import sys
from notelist.app import app


HOST_KEY = "--host"
PORT_KEY = "--port"


def get_arg_val(key: str):
    """Return the value of an argument.

    :param key: Argument key.
    :return: Argument value.
    """
    val = None

    if key in sys.argv:
        i = sys.argv.index(key)

        if i < len(sys.argv) - 1:
            val = sys.argv[i + 1]

    return val


def run():
    """Run the application."""
    host = get_arg_val(HOST_KEY)
    port = get_arg_val(PORT_KEY)

    if host and port:
        app.run(host=host, port=port)
    elif host:
        app.run(host=host)
    elif port:
        app.run(port=port)
    else:
        app.run()
