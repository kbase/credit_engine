"""Error messages and message generation functions."""

import json
from typing import Any

ERROR_STRING = {
    "doi_list_format": "DOI list must be a list of strings with non-zero length",
    "no_valid_dois": "No valid DOIs found in doi list",
    "missing_required": "Missing required argument",
    "http_error": "HTTP request failed",
    "invalid_param": "Invalid parameter",
    "generic": "An unspecified error has occurred",
}


def make_error(err_type: str = "", args: dict[str, Any] | None = None) -> str:
    """Generate a lovely error message.

    :param err_type: error type, defaults to ""
    :type err_type: str, optional
    :param args: arguments to the error, defaults to None
    :type args: dict[str, Any] | None, optional
    :return: error message string
    :rtype: str
    """
    if isinstance(args, dict) and args:
        error_with_args = {
            "missing_required": f"Missing required argument: {args.get('required', 'REQUIRED')}",
            "http_error": f"Request for {args.get('doi', 'DOI')} failed with status code {args.get('status_code', 'STATUS_CODE')}",
            "invalid_param": f"Invalid {args.get('param', 'parameter')}: \"{args.get(args.get('param', None), json.dumps(args, sort_keys=True))}\"",
        }
        if err_type in error_with_args:
            return error_with_args[err_type]

    return ERROR_STRING.get(err_type, ERROR_STRING["generic"])
