from urllib.parse import quote

from credit_engine.util import full_path

DATACITE_SAMPLE_DATA_DIR = full_path("sample_data/datacite")


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
