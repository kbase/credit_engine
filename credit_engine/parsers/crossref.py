from urllib.parse import quote

from credit_engine.util import full_path

VALID_OUTPUT_FORMATS = ["json", "unixsd", "unixref"]
CROSSREF_SAMPLE_DATA_DIR = full_path("sample_data/crossref")
DEFAULT_EMAIL = "credit_engine@kbase.us"


def get_endpoint(
    doi: str = "", output_format: str = "json", email_address: str = DEFAULT_EMAIL
) -> str:
    """Get the appropriate endpoint for a CrossRef query.

    :param doi: DOI to retrieve
    :type doi: str
    :param output_format: desired format; one of 'unixsd', 'unixref', or 'json'; defaults to 'json'
    :type output_format: str, optional
    :param email_address: email address to query from, defaults to 'credit_engine@kbase.us'
    :type email_address: str, optional
    :return: full URL to query
    :rtype: str
    """
    if not doi:
        raise ValueError("Missing required argument: doi")

    lc_output_format = output_format.lower()
    if lc_output_format not in VALID_OUTPUT_FORMATS:
        raise ValueError(f"Invalid output format: {output_format}")

    if lc_output_format == "json":
        return f"https://api.crossref.org/works/{quote(doi)}"

    if not email_address:
        email_address = DEFAULT_EMAIL

    return f"https://doi.crossref.org/servlet/query?pid={email_address}&format={lc_output_format}&id={quote(doi)}"
