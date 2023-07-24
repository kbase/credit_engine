"""Crossref client.

access to the Crossref DOI endpoint
does not require authentication but does require
an email address for API access

API documentation:
    REST API (returns JSON): https://api.crossref.org/swagger-ui/index.html

    XML API: https://www.crossref.org/documentation/retrieve-metadata/xml-api/doi-to-metadata-query/
"""

from json import JSONDecodeError
from urllib.parse import quote

import requests
from pydantic import constr, validate_arguments

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.args import EmailClientArgs
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


class ClientArgs(EmailClientArgs):
    """Arguments for the Crossref client.

    :param EmailClientArgs: arguments
    :type EmailClientArgs: EmailClientArgs
    """


@validate_arguments
def get_endpoint(args: ClientArgs, doi: str, output_format: CE.OutputFormat) -> str:
    """Get the appropriate endpoint for a CrossRef query.

    :param args: arguments for DOI request
    :type args: ClientArgs
    :param doi: DOI to retrieve
    :type doi: str
    :param output_format: desired format, CE.OutputFormat.JSON or CE.OutputFormat.XML
    :type output_format: CE.OutputFormat
    :return: full URL to query
    :rtype: str
    """
    if output_format == CE.OutputFormat.JSON:
        return f"https://api.crossref.org/works/{quote(doi)}"

    quoted_email_address = quote(args.email_address)

    return f"https://doi.crossref.org/servlet/query?format=unixsd&id={quote(doi)}&pid={quoted_email_address}"


@validate_arguments
def retrieve_doi(
    args: ClientArgs, doi: str
) -> dict[str, dict | list | str | bytes | None]:
    """Fetch DOI data from Crossref.

    :param args: arguments for DOI request
    :type args: ClientArgs
    :param doi: the DOI to retrieve
    :type doi: str
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    doi_data = {}
    for fmt in args.output_formats:
        response = requests.get(get_endpoint(args, doi=doi, output_format=fmt))
        if response.status_code == 200:
            doi_data[fmt.value] = extract_data_from_resp(
                resp=response, fmt=fmt, doi=doi
            )
        else:
            print(
                f"Request for {doi} {fmt.value} failed with status code {response.status_code}"
            )
            doi_data[fmt.value] = None
    return doi_data


def extract_data_from_resp(
    # args: ClientArgs,
    doi: str,
    fmt: CE.OutputFormat,
    resp: requests.Response,
) -> dict | list | str | bytes | None:
    """Extract the data from a response object.

    :param args: arguments for DOI request
    :type args: ClientArgs
    :param doi: the relevant DOI
    :type doi: str
    :param fmt: format that the response was requested in
    :type fmt: CE.OutputFormat
    :param resp: response object for the DOI
    :type resp: requests.Response
    :return: decoded response content
    :rtype: dict | list | str | bytes | None
    """
    if fmt == CE.OutputFormat.JSON:
        try:
            return resp.json()
        except JSONDecodeError as e:
            print(f"Error decoding JSON for {doi}: " + str(e))
            return None
    return fix_line_endings(resp.content)


@validate_arguments
def check_doi_source(doi: constr(strip_whitespace=True, min_length=3)) -> str | None:
    """Check where a DOI is registered.

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
