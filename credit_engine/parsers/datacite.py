import base64
from typing import Any
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


def retrieve_doi(doi: str) -> requests.Response:
    """Fetch DOI data from DataCite.

    :param doi: the DOI to retrieve
    :type doi: str
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    response = requests.get(
        get_endpoint(doi),
        headers={
            "Accept": "application/vnd.api+json",
        },
    )
    if response.status_code == 200:
        return response

    raise ValueError(
        f"Request for {doi} failed with status code {response.status_code}"
    )


# def decode_xml(json_data: dict[str, Any]) -> dict[str, Any]:

#     try:
#         doi_xml = json_data["data"]["attributes"]["xml"]
#         if doi_xml:
#             decoded_xml = base64.b64decode(doi_xml)
#     except:
#         # do something
#         pass
