from json import JSONDecodeError
from typing import Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE
from credit_engine.errors import make_error

FILE_EXTENSIONS = {fmt: CE.EXT[fmt] for fmt in [CE.JSON, CE.XML]}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.OSTI}"
DEFAULT_FORMAT = CE.JSON


@validate_arguments
def get_endpoint(
    doi: CE.TrimmedString, output_format: Optional[CE.TrimmedString] = None
) -> str:
    """Get the URL for the OSTI endpoint.

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

    return f"https://www.osti.gov/api/v1/records?doi={quote(doi)}"


@validate_arguments
def retrieve_doi(
    doi: CE.TrimmedString,
    output_format_list: Optional[list[CE.TrimmedString]] = None,
) -> dict[str, Union[dict, list, bytes, None]]:
    """Fetch DOI data from OSTI.

    :param doi: the DOI to retrieve
    :type doi: str
    :param output_format_list: formats to retrieve the data in, defaults to None (i.e. JSON)
    :type output_format_list: list of strings, optional
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    if not output_format_list:
        output_format_list = [DEFAULT_FORMAT]

    doi_data = {}
    for fmt in output_format_list:
        response = requests.get(
            get_endpoint(doi),
            headers={
                "Accept": f"application/{fmt}",
            },
        )

        if response.status_code == 200:
            doi_data[fmt] = extract_data_from_resp(doi, response, fmt)
        else:
            # no results
            print(
                f"Request for {doi} {fmt} failed with status code {response.status_code}"
            )
            doi_data[fmt] = None

    return doi_data


def extract_data_from_resp(
    doi: str, resp: requests.Response, fmt: str
) -> Union[dict, list, bytes, None]:
    """Extract data from the API response.

    :param doi: DOI being fetched
    :type doi: str
    :param resp: response data
    :type resp: requests.Response
    :param fmt: format of the response
    :type fmt: str
    :return: _description_
    :rtype: Union[dict, list, bytes, None]
    """
    if fmt == "json":
        try:
            return resp.json()
        except JSONDecodeError as e:
            print(f"Error decoding JSON for {doi}: " + str(e))
            return None
    return resp.content
