from json import JSONDecodeError
from typing import Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE
from credit_engine.errors import make_error

FILE_EXTENSIONS = {fmt: CE.EXT[fmt] for fmt in [CE.JSON, CE.UNIXREF, CE.UNIXSD]}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.CROSSREF}"
DEFAULT_FORMAT = CE.JSON


@validate_arguments
def get_endpoint(
    doi: CE.TrimmedString,
    output_format: Optional[CE.TrimmedString] = None,
    email_address: Optional[CE.TrimmedString] = None,
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
    lc_output_format = output_format.lower() if output_format else DEFAULT_FORMAT

    if lc_output_format not in FILE_EXTENSIONS:
        raise ValueError(
            make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
            )
        )

    if lc_output_format == CE.JSON:
        return f"https://api.crossref.org/works/{quote(doi)}"

    quoted_email_address = (
        quote(email_address) if email_address else quote(CE.DEFAULT_EMAIL)
    )

    return f"https://doi.crossref.org/servlet/query?id={quote(doi)}&format={lc_output_format}&pid={quoted_email_address}"


@validate_arguments
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
            doi_data[fmt] = extract_data_from_resp(doi, response, fmt)
        else:
            print(
                f"Request for {doi} {fmt} failed with status code {response.status_code}"
            )
            doi_data[fmt] = None
    return doi_data


def extract_data_from_resp(
    doi: str, resp: requests.Response, fmt: str
) -> Union[dict, list, bytes, None]:
    """Extract the data from a response object.

    :param doi: the relevant DOI
    :type doi: str
    :param resp: response object for the DOI
    :type resp: requests.Response
    :param fmt: format that the response was requested in
    :type fmt: str
    :return: decoded response content
    :rtype: Union[dict, list, bytes, None]
    """
    if fmt == CE.JSON:
        try:
            return resp.json()
        except JSONDecodeError as e:
            print(f"Error decoding JSON for {doi}: " + str(e))
            return None
    return resp.content
