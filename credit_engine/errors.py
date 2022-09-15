from typing import Optional, Any


def make_error(err_type: str = "", args: Optional[dict[str, Any]] = None) -> str:
    if isinstance(args, dict) and len(args.keys()) > 0:
        print("running the error_with_args loop")
        print({"args": args, "args keys": args.keys(), "len args keys": len(args.keys())})
        ERROR_WITH_ARGS = {
            "missing_required": f"Missing required argument: {args.get('required', 'REQUIRED')}",
            "http_error": f"Request for {args.get('doi', 'DOI')} failed with status code {args.get('status_code', 'STATUS_CODE')}",
        }
        print(ERROR_WITH_ARGS)
        if err_type in ERROR_WITH_ARGS:
            return ERROR_WITH_ARGS[err_type]

    ERROR_STRING = {
        "doi_list_format": "DOI list must be a list of strings with non-zero length",
        "no_valid_dois": "No valid DOIs found in doi list",
        "missing_required": "Missing required argument",
        "http_error": "HTTP request failed",
    }
    return ERROR_STRING.get(err_type, "An unspecified error has occurred")
