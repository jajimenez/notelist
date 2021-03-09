"""Configuration module."""

from typing import Tuple, Optional
import userconf as uc

from notelist import tools


Config = Tuple[Optional[str], Optional[int], Optional[str]]
uc.set_application_id("notelist")

CONF_NOT_SET = (
    'Configuration parameters not defined.\nRun "notelist configure" to set '
    'the parameters.')

HOST_ID = "host"
PORT_ID = "port"
DB_URI_ID = "db_uri"

TITLE = "Notelist - Configuration"
DESC = "Please type each parameter value (without quotes) and press Enter:\n"
HOST_DESC = 'Host (e.g. "localhost", "127.0.0.1", "0.0.0.0"): '
PORT_DESC = "Port (e.g. 5000): "
DB_URI_DESC = 'Database URI (e.g. "sqlite:///data.db"): '


def get_config() -> Config:
    """Return the configuration values.

    :return: Dictionary containing the configuration values.
    """
    return (
        uc.get_setting_value(HOST_ID),
        uc.get_setting_value(PORT_ID),
        uc.get_setting_value(DB_URI_ID))


def config():
    """Open the configuration user interface.

    Parameters:
    - Host. E.g. "localhost", "127.0.0.1", "0.0.0.0".
    - Port. E.g. 5000.
    - Database URI. E.g. "sqlite:///data.db".
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

    uc.set_setting_value(HOST_ID, host)
    uc.set_setting_value(PORT_ID, port)
    uc.set_setting_value(DB_URI_ID, db_uri)
