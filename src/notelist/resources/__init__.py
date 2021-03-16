"""Package with the resources."""

from typing import Any, Dict, Optional, Union


Response = Dict[str, Union[str, Dict]]

OPERATION_NOT_ALLOWED = "Operation not allowed."
USER_UNAUTHORIZED = "User unauthorized."


def get_response_data(message: str, result: Optional[Dict] = None) -> Response:
    """Return the response data of a request.

    The data returned is a dictionary intended to be serialized as a JSON
    string and to be sent as the response text of the request.

    :param message: Message.
    :param result: Result (if any).
    :return: Dictionary with `message` and, optionally, `result`.
    """
    response = {"message": message}

    if result is not None:
        response["result"] = result

    return response
