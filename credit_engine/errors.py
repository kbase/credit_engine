import json
from typing import Any, Optional, Union

ERROR_STRING = {
    "doi_list_format": "DOI list must be a list of strings with non-zero length",
    "no_valid_dois": "No valid DOIs found in doi list",
    "missing_required": "Missing required argument",
    "http_error": "HTTP request failed",
    "invalid_param": "Invalid parameter",
    "generic": "An unspecified error has occurred",
}


def missing_required(args):
    required_args: Union[str, list[str]] = args.get("required", "REQUIRED")
    n_args = 1
    if isinstance(required_args, list):
        required_args.sort()
        required_args = ", ".join(required_args)
        n_args = len(required_args)

    return f"Missing required argument{'' if n_args == 1 else 's'}: {required_args}"


def make_error(err_type: str = "", args: Optional[dict[str, Any]] = None) -> str:
    if isinstance(args, dict) and args:
        ERROR_WITH_ARGS = {
            "missing_required": missing_required(args),
            "http_error": f"Request for {args.get('url', 'URL')} failed with status code {args.get('status_code', 'STATUS_CODE')}",
            "invalid_param": f"Invalid {args.get('param', 'parameter')}: {args.get(args.get('param', None), json.dumps(args, sort_keys=True))}",
        }
        if err_type in ERROR_WITH_ARGS:
            return ERROR_WITH_ARGS[err_type]

    return ERROR_STRING.get(err_type, ERROR_STRING["generic"])


def print_error(err_type: str = "", args: Optional[dict[str, Any]] = None) -> None:
    print(make_error(err_type, args))
