"""
DataCite client

access to the DataCite DOI endpoint
does not require authentication

API documentation: https://support.datacite.org/docs/api
"""

import base64
from json import JSONDecodeError
from typing import Any, Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE  # noqa: N812
from credit_engine.errors import make_error

NAME = "DataCite"
VALID_OUTPUT_FORMATS = {CE.OutputFormat.JSON, CE.OutputFormat.XML}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.DATACITE}"
DEFAULT_FORMAT = CE.OutputFormat.JSON

DATACITE_URI = "https://api.datacite.org/dois/"


@validate_arguments
def get_endpoint(
    doi: CE.TrimmedString, output_format: Optional[CE.OutputFormat] = None
) -> str:
    """Get the URL for the DataCite endpoint.

    :param doi: DOI to retrieve
    :type doi: CE.TrimmedString
    :param output_format: format to receive data in (N.b. URL is the
        same regardless of format)
    :type output_format: CE.OutputFormat
    :return: endpoint URI
    :rtype: str
    """
    if output_format and output_format not in VALID_OUTPUT_FORMATS:
        raise ValueError(
            make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
            )
        )

    return f"https://api.datacite.org/dois/{quote(doi)}?affiliation=true"


@validate_arguments
def retrieve_doi(
    doi: CE.TrimmedString,
    output_formats: Optional[set[CE.OutputFormat]] = None,
    **kwargs,
) -> dict[str, Union[dict, list, bytes, None]]:
    """
    Fetch DOI data from DataCite.

    :param doi: the DOI to retrieve
    :type doi: CE.TrimmedString
    :param output_formats: format(s) for the DOI
    :type output_formats: set[CE.OutputFormat], optional
    :raises ValueError: if the request returned an error
    :return: the decoded JSON response
    :rtype: dict
    """

    if not output_formats:
        output_formats = {DEFAULT_FORMAT}

    response = requests.get(
        get_endpoint(doi),
        headers={
            "Accept": "application/vnd.api+json",
        },
    )
    if response.status_code == 200:
        return extract_data_from_resp(doi, response, output_formats)

    # no results
    for fmt in output_formats:
        print(
            f"Request for {doi} {fmt.value} failed with status code {response.status_code}"
        )
    return {fmt: None for fmt in output_formats}


def extract_data_from_resp(
    doi: str, resp: requests.Response, output_formats: set[CE.OutputFormat]
) -> dict[str, Union[dict, list, bytes, None]]:
    """
    Extract the data from a Response object.

    :param doi: the DOI that has been fetched
    :type doi: str
    :param resp: response object for the DOI
    :type resp: requests.Response
    :param output_formats: formats requested for the DOI
    :type output_formats: set[CE.OutputFormat]
    :return: decoded response content
    :rtype: dict[str, Union[dict, list, bytes, None]]
    """

    doi_data: dict[str, Any] = {fmt.value: None for fmt in output_formats}
    resp_json = None
    try:
        resp_json = resp.json()
    except JSONDecodeError as e:
        print(f"Error decoding JSON for {doi}: " + str(e))
        return doi_data

    if CE.OutputFormat.JSON in output_formats:
        doi_data[CE.JSON] = resp_json

    if CE.OutputFormat.XML in output_formats:
        doi_data[CE.XML] = decode_xml(doi, resp_json)

    return doi_data


def decode_xml(doi: str, json_data: dict[str, Any]) -> Optional[bytes]:
    """Decode the encoded XML string in a DataCite response.

    :param doi: the relevant DOI
    :type doi: str
    :param json_data: the JSON response data
    :type json_data: dict[str, Any]
    :return: decoded XML (if it exists)
    :rtype: Optional[bytes]
    """
    if json_data.get("data", {}).get("attributes", {}).get("xml") is None:
        print(f"Error decoding XML for {doi}: XML node not found")
        return None
    doi_xml = json_data["data"]["attributes"]["xml"]
    try:
        if doi_xml:
            return base64.b64decode(doi_xml)
    except Exception as e:
        print(f"Error base64 decoding XML for {doi}: {str(e)}")
    return None
