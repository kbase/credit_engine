from pathlib import Path
from typing import Optional, Union
from urllib.parse import quote

import requests

from credit_engine.util import (
    clean_doi_list,
    save_data_to_file,
)

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


def retrieve_doi_list(
    doi_list: list[str],
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = SAMPLE_DATA_DIR,
    # TODO: add translate_xml option
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
            # except FileNotFoundError as e:
            #     print(e)

    return results
