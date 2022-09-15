from typing import Optional, Any


ERROR_STRING = {
    "doi_list_format": "DOI list must be a list of strings with non-zero length",
    "no_valid_dois": "No valid DOIs found in doi list",
    "missing_required": "Missing required argument",
    "http_error": "HTTP request failed",
    "invalid": "Invalid output format",
    "generic": "An unspecified error has occurred",
}


def make_error(err_type: str = "", args: Optional[dict[str, Any]] = None) -> str:
    if isinstance(args, dict) and args:
        ERROR_WITH_ARGS = {
            "missing_required": f"Missing required argument: {args.get('required', 'REQUIRED')}",
            "http_error": f"Request for {args.get('doi', 'DOI')} failed with status code {args.get('status_code', 'STATUS_CODE')}",
            "invalid": f"Invalid output format: {args.get('format', 'FORMAT')}",
        }
        if err_type in ERROR_WITH_ARGS:
            return ERROR_WITH_ARGS[err_type]

    return ERROR_STRING.get(err_type, ERROR_STRING["generic"])
