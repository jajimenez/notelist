"""Package with the resources."""

from typing import Optional, Union, Any, List, Dict


Result = Optional[Union[Dict, List[Dict]]]
Response = Dict[str, Union[str, Dict]]

VALIDATION_ERROR = "Validation error: {}."
OPERATION_NOT_ALLOWED = "Operation not allowed."
USER_UNAUTHORIZED = "User unauthorized."


def get_response_data(message: str, result: Result = None) -> Response:
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
