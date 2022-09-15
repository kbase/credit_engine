from urllib.parse import quote


def get_endpoint(doi: str = "") -> str:
    """Get the URL for the OSTI endpoint.

    :param doi: DOI to retrieve
    :type doi: str
    :return: endpoint URI
    :rtype: str
    """
    if not doi:
        raise ValueError("Missing required argument: doi")
    return f"https://www.osti.gov/api/v1/records/{quote(doi)}"
