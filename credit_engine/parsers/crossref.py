from typing import Optional, Union
from urllib.parse import quote

import requests

import credit_engine.constants as CE
from credit_engine.errors import make_error

FILE_EXTENSIONS = {fmt: CE.EXT[fmt] for fmt in [CE.JSON, CE.UNIXREF, CE.UNIXSD]}
SAMPLE_DATA_DIR = f"sample_data/{CE.CROSSREF}"
DEFAULT_EMAIL = "credit_engine@kbase.us"
DEFAULT_FORMAT = CE.JSON


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
    if lc_output_format not in FILE_EXTENSIONS:
        raise ValueError(
            make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
            )
        )

    if lc_output_format == "json":
        return f"https://api.crossref.org/works/{quote(doi)}"

    if not email_address:
        email_address = DEFAULT_EMAIL

    return f"https://doi.crossref.org/servlet/query?pid={email_address}&format={lc_output_format}&id={quote(doi)}"


def retrieve_doi(
    doi: str,
    output_format_list: Optional[list[str]] = None,
    email_address: Optional[str] = None,
) -> dict[str, Union[dict, list, bytes, None]]:
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
    if not output_format_list:
        output_format_list = [DEFAULT_FORMAT]

    doi_data = {}
    for fmt in output_format_list:
        response = requests.get(get_endpoint(doi, fmt, email_address))
        if response.status_code == 200:
            doi_data[fmt] = extract_data_from_resp(response, fmt)
        else:
            print(
                f"Request for {doi} {fmt} failed with status code {response.status_code}"
            )
            doi_data[fmt] = None
    return doi_data


def extract_data_from_resp(
    resp: requests.Response, fmt: str
) -> Union[dict, list, bytes, None]:
    if fmt == "json":
        try:
            return resp.json()
        except Exception as e:
            print(e)
            return None
    return resp.content
