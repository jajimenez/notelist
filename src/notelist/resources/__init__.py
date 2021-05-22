"""Package with the resources."""

from typing import Optional, Union, Any, List, Dict


Result = Optional[Union[Dict, List[Dict]]]
Response = Dict[str, Union[str, Dict]]

# Codes 401 and 422 can be returned in all the endpoints that have user
# authentication.
RESPONSE_STATUS = {
    200: "Success",
    201: "Success",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    422: "Unprocessable Entity"}

VALIDATION_ERROR = "Validation error: {}."
OPERATION_NOT_ALLOWED = "Operation not allowed."
USER_UNAUTHORIZED = "User unauthorized."


def get_response_codes(*codes: int) -> Dict[int, str]:
    """Return a dictionary contaning HTTP response status codes and names.

    :param codes: Status codes.
    :return: Dictionary with the status codes and the names of `codes`.
    """
    return {c: RESPONSE_STATUS[c] for c in codes}


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
