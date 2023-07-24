"""OSTI client for access to the OSTI records endpoint.

Does not require authentication. It is recommended that the OSTI elink
client is used instead as the schema is more comprehensive.

Although the OSTI endpoint supports XML, this client only deals with JSON,
and XML requests will return an error.

API documentation: https://www.osti.gov/api/v1/docs
"""

from json import JSONDecodeError
from urllib.parse import quote

import requests
from pydantic import Field, validate_arguments

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.args import GenericClientArgs

NAME = "OSTI"
SAMPLE_DATA_DIR = f"{CE.SAMPLE_DATA}/{CE.OSTI}"


class ClientArgs(GenericClientArgs):
    """Arguments for the OSTI non-authenticated client.

    :param GenericClientArgs: arguments
    :type GenericClientArgs: GenericClientArgs
    """

    VALID_OUTPUT_FORMATS: set[CE.OutputFormat] = Field(
        {CE.OutputFormat.JSON}, const=True
    )
    output_formats: set[CE.OutputFormat] = Field(default={CE.OutputFormat.JSON})


@validate_arguments
def get_endpoint(doi: str) -> str:
    """Get the URL for the OSTI endpoint.

    :param doi: the relevant DOI
    :type doi: str
    :return: endpoint URI
    :rtype: str
    """
    return f"https://www.osti.gov/api/v1/records?doi={quote(doi)}"


@validate_arguments
def retrieve_doi(args: ClientArgs, doi: str) -> dict[str, dict | list | None]:
    """Fetch DOI data from OSTI.

    :param args: arguments for DOI request
    :type args: ClientArgs
    :param doi: the relevant DOI
    :type doi: str
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    doi_data = {}
    for fmt in args.output_formats:
        response = requests.get(
            get_endpoint(doi=doi),
            headers={
                "Accept": f"application/{fmt.value}",
            },
        )

        if response.status_code == 200:
            doi_data[fmt.value] = extract_data_from_resp(resp=response, doi=doi)
        else:
            # no results
            print(
                f"Request for {doi} {fmt.value} failed with status code {response.status_code}"
            )
            doi_data[fmt.value] = None

    return doi_data


def extract_data_from_resp(
    resp: requests.Response,
    doi: str,  # args: ClientArgs,
) -> dict | list | None:
    """Extract data from the API response.

    :param args: arguments for DOI request
    :type args: ClientArgs
    :param doi: the relevant DOI
    :type doi: str
    :param resp: response object for the DOI
    :type resp: requests.Response
    :return: parsed response
    :rtype: dict | list | None
    """
    if resp is None:
        return None

    try:
        return resp.json()
    except JSONDecodeError as e:
        print(f"Error decoding JSON for {doi}: " + str(e))
        return None
