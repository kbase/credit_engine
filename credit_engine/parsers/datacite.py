from urllib.parse import quote
import requests

VALID_OUTPUT_FORMATS = ["json"]
SAMPLE_DATA_DIR = "sample_data/datacite"


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
