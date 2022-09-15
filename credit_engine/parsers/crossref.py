import requests
from typing import Optional, Union
from pathlib import Path
from urllib.parse import quote
from credit_engine.errors import make_error

from credit_engine.util import (
    clean_doi_list,
    save_data_to_file,
)

VALID_OUTPUT_FORMATS = ["json", "unixsd", "unixref"]
SAMPLE_DATA_DIR = "sample_data/crossref"
DEFAULT_EMAIL = "credit_engine@kbase.us"
DEFAULT_FORMAT = "json"


def get_endpoint(
    doi: str = "",
    output_format: Optional[str] = DEFAULT_FORMAT,
    email_address: Optional[str] = DEFAULT_EMAIL,
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
        raise ValueError(make_error("missing_required", {"required": "doi"}))

    if not output_format:
        output_format = DEFAULT_FORMAT

    lc_output_format = output_format.lower()
    if lc_output_format not in VALID_OUTPUT_FORMATS:
        raise ValueError(make_error("invalid", {"format": output_format}))

    if lc_output_format == "json":
        return f"https://api.crossref.org/works/{quote(doi)}"

    if not email_address:
        email_address = DEFAULT_EMAIL

    return f"https://doi.crossref.org/servlet/query?pid={email_address}&format={lc_output_format}&id={quote(doi)}"


def retrieve_doi(
    doi: str,
    output_format: Optional[str] = None,
    email_address: Optional[str] = None,
) -> requests.Response:
    """Fetch DOI data from Crossref.

    :param doi: the DOI to retrieve
    :type doi: str
    :param output_format_list: formats to retrieve the data in, defaults to None (i.e. JSON)
    :type output_format_list: list of strings, optional
    :param email_address: email address to query from, defaults to 'credit_engine@kbase.us'
    :type email_address: str, optional
    :raises ValueError: if the request returned anything other than a 200
    :return: the decoded JSON response
    :rtype: dict
    """
    response = requests.get(get_endpoint(doi, output_format, email_address))
    if response.status_code == 200:
        return response

    raise ValueError(
        f"Request for {doi} failed with status code {response.status_code}"
    )


def retrieve_doi_list(
    doi_list: list[str],
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = SAMPLE_DATA_DIR,
    # TODO: add output_format_list option
) -> dict[str, dict]:
    """Retrieve a list of DOIs from DataCite.

    :param doi_list: list of DOIs to retrieve
    :type doi_list: list[str]
    :param save_files: whether or not to save the data to disk, defaults to False
    :type save_files: bool, optional
    :param save_dir: the directory to save files to, defaults to SAMPLE_DATA_DIR
    :type save_dir: Optional[Union[Path, str]], optional
    :return: a dictionary with two keys, 'data', where the DOI json is stored, and
    'files', containing a mapping of DOI to file path for saved data
    :rtype: dict[str, dict]
    """

    cleaned_doi_list = clean_doi_list(doi_list)
    if not save_dir:
        # use the sample dir
        save_dir = SAMPLE_DATA_DIR

    results = {
        "data": {},
    }

    if save_files:
        results["files"] = {}

    for doi in cleaned_doi_list:
        try:
            resp = retrieve_doi(doi)

        except ValueError as e:
            print(e)
            continue

        results["data"][doi] = resp.json()

        if save_files:
            save_data_to_file(
                doi=doi,
                save_dir=save_dir,
                suffix="json",
                resp=resp,
                result_data=results,
            )
            # doi_file = Path(save_dir).joinpath(f"{doi_to_file_name(doi)}.json")
            # try:
            #     write_to_file(doi_file, resp.json())
            #     results["files"][doi] = doi_file
            # except OSError as e:
            #     print(e)

    return results
