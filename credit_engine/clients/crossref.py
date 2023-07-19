"""
Crossref client

access to the Crossref DOI endpoint
does not require authentication but does require
an email address for API access

API documentation:
    REST API (returns JSON): https://api.crossref.org/swagger-ui/index.html

    XML API: https://www.crossref.org/documentation/retrieve-metadata/xml-api/doi-to-metadata-query/
"""

from enum import Enum
from json import JSONDecodeError
from typing import Optional, Union
from urllib.parse import quote

import requests
from pydantic import EmailStr, constr, validate_arguments

import credit_engine.constants as CE  # noqa: N812
from credit_engine.errors import make_error
from credit_engine.util import fix_line_endings

NAME = "Crossref"

VALID_OUTPUT_FORMATS = {
    CE.OutputFormat.JSON,
    CE.OutputFormat.XML,
}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.CROSSREF}"
DEFAULT_FORMAT = CE.OutputFormat.JSON


CROSSREF_REST_URI = "https://api.crossref.org/"
CROSSREF_XML_URI = "https://doi.crossref.org/servlet/query"


@validate_arguments
def get_endpoint(
    doi: CE.TrimmedString,
    output_format: Optional[CE.OutputFormat] = None,
    email_address: Optional[EmailStr] = None,
) -> str:
    """Get the appropriate endpoint for a CrossRef query.

    :param doi: DOI to retrieve
    :type doi: str
    :param output_format: desired format, CE.OutputFormat.JSON or CE.OutputFormat.XML; defaults to JSON
    :type output_format: str, optional
    :param email_address: email address to query from, defaults to 'credit_engine@kbase.us'
    :type email_address: EmailStr, optional
    :return: full URL to query
    :rtype: str
    """
    if not output_format:
        output_format = DEFAULT_FORMAT
    elif output_format not in VALID_OUTPUT_FORMATS:
        raise ValueError(
            make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
            )
        )

    if output_format == CE.OutputFormat.JSON:
        return f"https://api.crossref.org/works/{quote(doi)}"

    quoted_email_address = (
        quote(email_address) if email_address else quote(CE.DEFAULT_EMAIL)
    )

    return f"https://doi.crossref.org/servlet/query?format=unixsd&id={quote(doi)}&pid={quoted_email_address}"


@validate_arguments
def retrieve_doi(
    doi: CE.TrimmedString,
    output_formats: Optional[set[CE.OutputFormat]] = None,
    email_address: Optional[EmailStr] = None,
    **kwargs,
) -> dict[str, Union[dict, list, str, bytes, None]]:
    """Fetch DOI data from Crossref.

    :param doi: the DOI to retrieve
    :type doi: str
    :param output_formats: formats to retrieve the data in, defaults to None (i.e. JSON)
    :type output_formats: set of strings, optional
    :param email_address: email address to query from, defaults to 'credit_engine@kbase.us'
    :type email_address: str, optional
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    if not output_formats:
        output_formats = {DEFAULT_FORMAT}

    doi_data = {}
    for fmt in output_formats:
        response = requests.get(get_endpoint(doi, fmt, email_address))
        if response.status_code == 200:
            doi_data[fmt] = extract_data_from_resp(doi, response, fmt)
        else:
            print(
                f"Request for {doi} {fmt.value} failed with status code {response.status_code}"
            )
            doi_data[fmt] = None
    return doi_data


def extract_data_from_resp(
    doi: str, resp: requests.Response, fmt: str
) -> Union[dict, list, str, bytes, None]:
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
    return fix_line_endings(resp.content)


@validate_arguments
def check_doi_source(doi: constr(strip_whitespace=True, min_length=3)) -> str | None:
    """Check whether a DOI is accessible via CrossRef.

    :param doi: digital object identifier
    :type doi: str
    :return: ID of the agency from which the data can be retrieved
    :rtype: str | None
    """
    resp = requests.get(f"https://api.crossref.org/works/{quote(doi)}/agency")
    if resp.status_code == 200:
        payload = resp.json()
        agency = payload.get("message", {}).get("agency", {}).get("id", "unknown")
        print(f"doi {doi} at {agency}")
        return agency

    return None
