"""DataCite client.

access to the DataCite DOI endpoint
does not require authentication

API documentation: https://support.datacite.org/docs/api
"""

import base64
from json import JSONDecodeError
from typing import Any
from urllib.parse import quote

import requests
from pydantic import Field, validate_arguments

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.args import GenericClientArgs

NAME = "DataCite"
VALID_OUTPUT_FORMATS = {CE.OutputFormat.JSON, CE.OutputFormat.XML}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.DATACITE}"
DEFAULT_FORMAT = CE.OutputFormat.JSON

DATACITE_URI = "https://api.datacite.org/dois/"


class ClientArgs(GenericClientArgs):
    """Arguments for the DataCite client.

    :param GenericClientArgs: arguments
    :type GenericClientArgs: GenericClientArgs
    """

    output_formats: set[CE.OutputFormat] = Field(default={CE.OutputFormat.JSON})


@validate_arguments
def get_endpoint(doi: str) -> str:
    """Get the URL for the DataCite endpoint.

    :param doi: DOI to retrieve
    :type doi: str
    :return: endpoint URI
    :rtype: str
    """
    return f"https://api.datacite.org/dois/{quote(doi)}?affiliation=true"


@validate_arguments
def retrieve_doi(
    args: ClientArgs,
    doi: str,
) -> dict[str, dict | list | bytes | str | None]:
    """Fetch DOI data from DataCite.

    :param args: arguments for DOI request
    :type doi: ClientArgs
    :param doi: the relevant DOI
    :type doi: str
    :raises ValueError: if the request returned an error
    :return: the decoded JSON response
    :rtype: dict
    """
    response = requests.get(
        get_endpoint(doi=doi),
        headers={
            "Accept": "application/vnd.api+json",
        },
    )
    if response.status_code == 200:
        return extract_data_from_resp(doi=doi, resp=response, args=args)

    # no results
    for fmt in args.output_formats:
        print(
            f"Request for {doi} {fmt.value} failed with status code {response.status_code}"
        )
    return {fmt.value: None for fmt in args.output_formats}


def extract_data_from_resp(
    args: ClientArgs, doi: str, resp: requests.Response
) -> dict[str, dict | list | bytes | str | None]:
    """Extract the data from a Response object.

    :param args: arguments for DOI request
    :type args: ClientArgs
    :param doi: the relevant DOI
    :type doi: str
    :param resp: response object for the DOI
    :type resp: requests.Response
    :return: decoded response content
    :rtype: dict[str, Union[dict, list, bytes, None]]
    """
    doi_data: dict[str, Any] = {fmt.value: None for fmt in args.output_formats}
    resp_json = None
    try:
        resp_json = resp.json()
    except JSONDecodeError as e:
        print(f"Error decoding JSON for {doi}: " + str(e))
        return doi_data

    if CE.OutputFormat.JSON in args.output_formats:
        doi_data[CE.OutputFormat.JSON.value] = resp_json

    if CE.OutputFormat.XML in args.output_formats:
        doi_data[CE.OutputFormat.XML.value] = decode_xml(doi=doi, json_data=resp_json)

    return doi_data


def decode_xml(doi: str, json_data: dict[str, Any]) -> bytes | None:
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
        print(f"Error base64 decoding XML for {doi}: {e!s}")
    return None
