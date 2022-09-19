import base64
from typing import Any, Optional, Union
from urllib.parse import quote

import requests

FILE_EXTENSIONS = {"xml": "xml", "json": "json"}
SAMPLE_DATA_DIR = "sample_data/datacite"
DEFAULT_FORMAT = "json"


def get_endpoint(doi: str = "") -> str:
    """Get the URL for the DataCite endpoint.

    :param doi: DOI to retrieve
    :type doi: str
    :return: endpoint URI
    :rtype: str
    """
    if not doi:
        raise ValueError("Missing required argument: doi")
    return f"https://api.datacite.org/dois/{quote(doi)}?affiliation=true"


def retrieve_doi(
    doi: str,
    output_format_list: Optional[list[str]] = None,
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
        return extract_data_from_resp(response, output_format_list)

    # no results
    for fmt in output_format_list:
        print(f"Request for {doi} {fmt} failed with status code {response.status_code}")
    return {fmt: None for fmt in output_format_list}


def extract_data_from_resp(
    resp: requests.Response, output_format_list: list[str]
) -> dict[str, Union[dict, list, bytes, None]]:

    doi_data = {fmt: None for fmt in output_format_list}
    resp_json = None
    try:
        resp_json = resp.json()
    except Exception as e:
        print(e)
        return doi_data

    if "json" in output_format_list:
        doi_data["json"] = resp_json

    if "xml" in output_format_list:
        doi_data["xml"] = decode_xml(resp_json)

    return doi_data


def decode_xml(json_data: dict[str, Any]) -> Optional[bytes]:
    try:
        doi_xml = json_data["data"]["attributes"]["xml"]
        if doi_xml:
            return base64.b64decode(doi_xml)
    except Exception as e:
        print(e)
    return None
