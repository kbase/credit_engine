"""
OSTI client for access to the OSTI records endpoint.

Does not require authentication. It is recommended that the OSTI elink
client is used instead as the schema is more comprehensive.

Although the OSTI endpoint supports XML, this client only deals with JSON,
and XML requests will return an error.

API documentation: https://www.osti.gov/api/v1/docs
"""

from json import JSONDecodeError
from typing import Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE  # noqa: N812
from credit_engine.errors import make_error
from credit_engine.util import fix_line_endings

NAME = "OSTI"
VALID_OUTPUT_FORMATS = {CE.OutputFormat.JSON, CE.OutputFormat.XML}
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.OSTI}"
DEFAULT_FORMAT = CE.OutputFormat.JSON


@validate_arguments
def get_endpoint(
    doi: CE.TrimmedString, output_format: Optional[CE.OutputFormat] = None
) -> str:
    """Get the URL for the OSTI endpoint.

    :param doi: DOI to retrieve
    :type doi: str
    :param output_format: format to receive data in (N.b. URL is the
        same regardless of format)
    :type output_format: CE.OutputFormat
    :return: endpoint URI
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

    return f"https://www.osti.gov/api/v1/records?doi={quote(doi)}"


@validate_arguments
def retrieve_doi(
    doi: CE.TrimmedString,
    output_formats: Optional[set[CE.OutputFormat]] = None,
) -> dict[str, Union[dict, list, bytes, None]]:
    """Fetch DOI data from OSTI.

    :param doi: the DOI to retrieve
    :type doi: str
    :param output_formats: format to retrieve the data in, defaults to None (i.e. JSON)
    :type output_formats: set[CE.OutputFormat], optional
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    if not output_formats:
        output_formats = {DEFAULT_FORMAT}

    doi_data = {}
    for fmt in output_formats:
        response = requests.get(
            get_endpoint(doi, fmt),
            headers={
                "Accept": f"application/{fmt.value}",
            },
        )

        if response.status_code == 200:
            doi_data[fmt] = extract_data_from_resp(doi, response, fmt)
        else:
            # no results
            print(
                f"Request for {doi} {fmt.value} failed with status code {response.status_code}"
            )
            doi_data[fmt] = None

    return doi_data


def extract_data_from_resp(
    doi: CE.TrimmedString, resp: requests.Response, fmt: CE.OutputFormat
) -> Union[dict, list, str, bytes, None]:
    """Extract data from the API response.

    :param doi: DOI being fetched
    :type doi: CE.TrimmedString
    :param resp: response data
    :type resp: requests.Response
    :param fmt: format of the response
    :type fmt: CE.OutputFormat
    :return: parsed response
    :rtype: Union[dict, list, bytes, None]
    """
    if resp is None:
        return None

    if fmt == CE.OutputFormat.JSON:
        try:
            return resp.json()
        except JSONDecodeError as e:
            print(f"Error decoding JSON for {doi}: " + str(e))
            return None

    return fix_line_endings(resp.content)
