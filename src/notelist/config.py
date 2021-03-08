"""Configuration module."""

from typing import Tuple, Optional
import userconf as uc


Config = Tuple[Optional[str], Optional[int], Optional[str]]
uc.set_application_id("notelist")

HOST_ID = "host"
PORT_ID = "port"
DB_URI_ID = "db_uri"

TITLE = "Notelist configuration"
DESC = "Please type the following parameter values."


def get_config() -> Config:
    """Return the configuration values.

    :return: Dictionary containing the configuration values.
    """
    return (
        uc.get_setting_value(HOST_ID),
        uc.get_setting_value(PORT_ID),
        uc.get_setting_value(DB_URI_ID))


def config():
    """Set the configuration values.

    Parameters:
    - Host. E.g. "localhost", "127.0.0.1", "0.0.0.0".
    - Port. E.g. 5000.
    - Database URI. E.g. "sqlite:///data.db", "postgresql:///".
    """
    border = f'+{"-" * (len(TITLE) + 2)}+'

    print(f"\n{border}")
    print(f"| {TITLE} |")
    print(f"{border}\n")

    print("Please type the following parameter values (without quotes):\n")
    host = input('Host (e.g. "localhost", "127.0.0.1", "0.0.0.0"): ')

    if host == "":
        host = None

    while True:
        port = input("Port (e.g. 5000): ")

        try:
            port = int(port) if port != "" else None
            break
        except ValueError:
            print("Invalid value.")

    db_uri = input('Database URI (e.g. "sqlite:///data.db"): ')

    if db_uri == "":
        db_uri = None

    uc.set_setting_value(HOST_ID, host)
    uc.set_setting_value(PORT_ID, port)
    uc.set_setting_value(DB_URI_ID, db_uri)

    print()
