import requests
from typing import Optional
from urllib.parse import quote
from credit_engine.errors import make_error

VALID_OUTPUT_FORMATS = ["json", "unixsd", "unixref"]
SAMPLE_DATA_DIR = "sample_data/crossref"
DEFAULT_EMAIL = "credit_engine@kbase.us"
DEFAULT_FORMAT = "json"


def get_endpoint(
    doi: str = "",
    output_format: Optional[str] = DEFAULT_FORMAT,
    email_address: Optional[str] = DEFAULT_EMAIL,
) -> str:
    """Get the appropriate endpoint for a CrossRef query.

    :param doi: DOI to retrieve
    :type doi: str
    :param output_format: desired format; one of 'unixsd', 'unixref', or 'json'; defaults to 'json'
    :type output_format: str, optional
    :param email_address: email address to query from, defaults to 'credit_engine@kbase.us'
    :type email_address: str, optional
    :return: full URL to query
    :rtype: str
    """
    if not doi:
        raise ValueError(make_error("missing_required", {"required": "doi"}))

    if not output_format:
        output_format = DEFAULT_FORMAT

    lc_output_format = output_format.lower()
    if lc_output_format not in VALID_OUTPUT_FORMATS:
        raise ValueError(make_error("invalid", {"format": output_format}))

    if lc_output_format == "json":
        return f"https://api.crossref.org/works/{quote(doi)}"

    if not email_address:
        email_address = DEFAULT_EMAIL

    return f"https://doi.crossref.org/servlet/query?pid={email_address}&format={lc_output_format}&id={quote(doi)}"


def retrieve_doi(
    doi: str,
    output_format: Optional[str] = None,
    email_address: Optional[str] = None,
) -> requests.Response:
    """Fetch DOI data from Crossref.

    :param doi: the DOI to retrieve
    :type doi: str
    :param output_format_list: formats to retrieve the data in, defaults to None (i.e. JSON)
    :type output_format_list: list of strings, optional
    :param email_address: email address to query from, defaults to 'credit_engine@kbase.us'
    :type email_address: str, optional
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    response = requests.get(get_endpoint(doi, output_format, email_address))
    if response.status_code == 200:
        return response

    raise ValueError(
        f"Request for {doi} failed with status code {response.status_code}"
    )
