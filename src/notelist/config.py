"""Configuration module."""

from typing import Optional
import userconf as uc


# Application ID
uc.set_application_id("notelist")

# Setting keys
DB_URI_KEY = "db_uri"
ROOT_IP_KEY = "root_initial_password"


def get_conf_path() -> str:
    """Return the configuration file path.

    :return: File path.
    """
    return uc._app_set_file


def get_val(key: str) -> Optional[str]:
    """Return the value of a setting.

    :param key: Setting key.
    :return: Setting value.
    """
    val = uc.get_setting_value(key)

    # If the value is None, the configuration file might not exist. To make
    # sure that the configuration file exists, we set the value as an empty
    # string, as the "set_setting_value" function creates the file if it
    # doesn't exist.
    if val is None:
        uc.set_setting_value(key, "")

    return val


def set_val(key: str, val: Optional[str]):
    """Set the value of a setting.

    :param key: Setting key.
    :param val: Setting value.
    """
    return uc.set_setting_value(key, val)
