from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import quote

import requests

import credit_engine.parsers.crossref as crossref
import credit_engine.parsers.datacite as datacite
import credit_engine.util as util
from credit_engine.errors import make_error

DATA = "data"
FILES = "files"


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


def get_extension(parser, output_format: str = "json") -> str:
    """Get the appropriate file extension for saving data.

    :param parser: the appropriate parser for the data source
    :type parser: module
    :param output_format: format of data to be saved, defaults to 'json'
    :type output_format: str, optional
    :raises ValueError: if the output format is not valid for that parser
    :return: file extension
    :rtype: str
    """
    lc_output_format = output_format.lower()
    if lc_output_format not in parser.FILE_EXTENSIONS:
        raise ValueError(make_error("invalid", {"format": output_format}))
    return parser.FILE_EXTENSIONS[lc_output_format]


def retrieve_doi_list(
    doi_list: List[str],
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = None,
    source: Optional[str] = None,
    output_format_list: Optional[list[str]] = None,
) -> dict:
    """Retrieve a DOI, optionally saving it to a file

    :param doi: a list of DOIs to retrieve
    :type doi: str
    :return: a dictionary
    :rtype: dict
    """
    # validate_input(doi_list, save_files, save_dir, source, output_format_list)
    cleaned_doi_list = util.clean_doi_list(doi_list)

    if source == "datacite":
        parser = datacite
    elif source == "crossref":
        parser = crossref
    else:
        raise ValueError(f"Invalid data source: {source}")

    if output_format_list:
        # ensure the validity of the file format(s)
        invalid_formats = [
            fmt for fmt in output_format_list if fmt not in parser.FILE_EXTENSIONS
        ]
        if invalid_formats:
            raise ValueError(make_error("invalid", {"format": invalid_formats}))
    else:
        output_format_list = [parser.DEFAULT_FORMAT]

    if not save_dir:
        # use the sample dir
        save_dir = parser.SAMPLE_DATA_DIR

    results = {
        DATA: {},
    }

    if save_files:
        results[FILES] = {}

    for doi in cleaned_doi_list:
        results[DATA][doi] = parser.retrieve_doi(
            doi, output_format_list=output_format_list
        )

        if save_files:
            for fmt in output_format_list:
                if results[DATA][doi][fmt] is not None:
                    doi_file = util.save_data_to_file(
                        doi=doi,
                        save_dir=save_dir,
                        suffix=get_extension(parser, fmt),
                        data=results[DATA][doi][fmt],
                    )
                    if doi_file:
                        if doi not in results[FILES]:
                            results[FILES][doi] = {fmt: doi_file}
                        else:
                            results[FILES][doi][fmt] = doi_file

    return results
