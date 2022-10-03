import base64
from json import JSONDecodeError
from typing import Any, Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE
from credit_engine.errors import make_error

FILE_EXTENSIONS = {fmt: CE.EXT[fmt] for fmt in [CE.JSON, CE.XML]}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.DATACITE}"
DEFAULT_FORMAT = CE.JSON


@validate_arguments
def get_endpoint(
    doi: CE.TrimmedString, output_format: Optional[CE.TrimmedString] = None
) -> str:
    """Get the URL for the DataCite endpoint.

    :param doi: DOI to retrieve
    :type doi: str
    :param output_format: format to receive data in (N.b. URL is the
        same regardless of format)
    :type output_format: str
    :return: endpoint URI
    :rtype: str
    """
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

    return f"https://api.datacite.org/dois/{quote(doi)}?affiliation=true"


@validate_arguments
def retrieve_doi(
    doi: CE.TrimmedString,
    output_format_list: Optional[list[CE.TrimmedString]] = None,
) -> dict[str, Union[dict, list, bytes, None]]:
    """Fetch DOI data from DataCite.

    :param doi: the DOI to retrieve
    :type doi: str
    :param output_format_list: format(s) for the DOI
    :type output_format_list: list[str]
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """

    if not output_format_list:
        output_format_list = [DEFAULT_FORMAT]

    response = requests.get(
        get_endpoint(doi),
        headers={
            "Accept": "application/vnd.api+json",
        },
    )
    if response.status_code == 200:
        return extract_data_from_resp(doi, response, output_format_list)

    # no results
    for fmt in output_format_list:
        print(f"Request for {doi} {fmt} failed with status code {response.status_code}")
    return {fmt: None for fmt in output_format_list}


def extract_data_from_resp(
    doi: str, resp: requests.Response, output_format_list: list[str]
) -> dict[str, Union[dict, list, bytes, None]]:

    doi_data: dict[str, Any] = {fmt: None for fmt in output_format_list}
    resp_json = None
    try:
        resp_json = resp.json()
    except JSONDecodeError as e:
        print(f"Error decoding JSON for {doi}: " + str(e))
        return doi_data

    if "json" in output_format_list:
        doi_data["json"] = resp_json

    if "xml" in output_format_list:
        doi_data["xml"] = decode_xml(doi, resp_json)

    return doi_data


def decode_xml(doi: str, json_data: dict[str, Any]) -> Optional[bytes]:
    if json_data.get("data", {}).get("attributes", {}).get("xml", None) is None:
        print(f"Error decoding XML for {doi}: XML node not found")
        return None
    doi_xml = json_data["data"]["attributes"]["xml"]
    try:
        if doi_xml:
            return base64.b64decode(doi_xml)
    except Exception as e:
        print(f"Error base64 decoding XML for {doi}: {str(e)}")
    return None
