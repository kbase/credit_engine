from typing import List, Optional
from urllib.parse import quote
import credit_engine.util as util
import credit_engine.parsers as parsers
import credit_engine.parsers.crossref as crossref
import credit_engine.parsers.datacite as datacite
from pathlib import Path
import requests


def check_doi_source(doi: str) -> Optional[str]:
    """Check whether a DOI is accessible via CrossRef

    :param doi: digital object identifier
    :type doi: str
    :return: ID of the agency from which the data can be retrieved
    :rtype: str | None
    """
    resp = requests.get(f"https://api.crossref.org/works/{quote(doi)}/agency")
    if resp.status_code == 200:
        payload = resp.json()
        agency = payload.get("message", {}).get("agency", {}).get("id", "unknown")
        print(f"doi {doi} at {agency}")
        return agency

    return None


def retrieve_doi_list(
    doi_list: List[str],
    save_files: bool = False,
    save_dir: Optional[str] = None,
    source: Optional[str] = None,
    output_format_list: Optional[list[str]] = None,
) -> dict:
    """Retrieve a DOI, optionally saving it to a file

    :param doi: a list of DOIs to retrieve
    :type doi: str
    :return: a dictionary
    :rtype: dict
    """
    cleaned_doi_list = util.clean_doi_list(doi_list)

    if source == 'datacite':
        parser = datacite
    elif source == "crossref":
        parser = crossref
    else:
        raise ValueError(f"Invalid data source: {source}")

    if not save_dir:
        # use the sample dir
        save_dir = parser.SAMPLE_DATA_DIR

    results = {
        "data": {},
    }

    if save_files:
        results["files"] = {}

    for doi in cleaned_doi_list:
        try:
            resp = parser.retrieve_doi(doi)

        except ValueError as e:
            print(e)
            continue

        results["data"][doi] = resp.json()

        if save_files:
            util.save_data_to_file(
                doi=doi,
                save_dir=save_dir,
                suffix="json",
                resp=resp,
                result_data=results,
            )

    return results
