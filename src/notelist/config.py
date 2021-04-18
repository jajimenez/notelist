"""Configuration module."""

from typing import Tuple, Optional
import userconf as uc

from notelist import tools


Config = Tuple[Optional[str], Optional[int], Optional[str]]
uc.set_application_id("notelist")

# Settings
HOST_SET = "host"
PORT_SET = "port"
DB_URI_SET = "db_uri"

# Strings
TITLE = "Notelist - Configuration"
DESC = "Please type each parameter value (without quotes) and press Enter:\n"
HOST_DESC = 'Host (e.g. "localhost", "127.0.0.1", "0.0.0.0"): '
PORT_DESC = "Port (e.g. 5000): "
DB_URI_DESC = 'Database URI (e.g. "sqlite:///<path>"): '


def get_config() -> Config:
    """Return the configuration values.

    :return: Dictionary containing the configuration values.
    """
    # Host
    host = uc.get_setting_value(HOST_SET)

    # Port
    port = uc.get_setting_value(PORT_SET)

    if port is not None:
        port = int(port)

    # DB URI
    db_uri = uc.get_setting_value(DB_URI_SET)

    return host, port, db_uri


def set_config(host: str, port: int, db_uri: str):
    """Set the configuration values.

    :param host: Host. E.g. "localhost", "127.0.0.1", "0.0.0.0".
    :param port: Port. E.g. 5000.
    :db_uri: DB URI. E.g. "sqlite:///<path>".
    """
    uc.set_setting_value(HOST_SET, host)
    uc.set_setting_value(PORT_SET, port)
    uc.set_setting_value(DB_URI_SET, db_uri)


def config():
    """Open the configuration user interface.

    Parameters:
    - Host. E.g. "localhost", "127.0.0.1", "0.0.0.0".
    - Port. E.g. 5000.
    - Database URI. E.g. "sqlite:///<path>".
    """
    print(f"{tools.get_border_title(TITLE)}\n")
    print(DESC)

    host = input(HOST_DESC)

    if host == "":
        host = None

    while True:
        port = input(PORT_DESC)

        try:
            port = int(port) if port != "" else None
            break
        except ValueError:
            print("Invalid value.")

    db_uri = input(DB_URI_DESC)

    if db_uri == "":
        db_uri = None

    set_config(host, port, db_uri)
