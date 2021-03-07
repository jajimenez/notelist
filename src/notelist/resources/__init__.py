"""Package with the resources."""

from typing import Dict, Optional, Union


Response = Dict[str, Union[str, Dict]]


def get_response_data(message: str, result: Optional[Dict] = None) -> Response:
    """Return the response data of a request.

    The data returned is a dictionary intended to be serialized as a JSON
    string and to be sent as the response text of the request.

    :param message: Message.
    :param result: Result (if any).
    :return: Dictionary with `message` and `result`.
    """
    return {
        "message": message,
        "result": result
    }
