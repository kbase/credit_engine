import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Callable, Optional, Union
from urllib.parse import quote
from errors import make_error


def encode_doi(doi: str) -> str:
    """Encodes any dodgy doi characters for use as an URL.
    See https://www.doi.org/doi_handbook/2_Numbering.html#2.5.2 for DOI encoding recs
    :param doi: the doi
    :type doi: str
    :return: encoded doi for URI usage
    :rtype: str
    """
    return quote(doi)


def clean_doi_list(doi_list: list[str]) -> list[str]:
    """Clean up a list of DOIs.

    Dedupe and remove blanks.

    :param doi_list: list of putative DOIs
    :type doi_list: list[str]
    :raises ValueError: if DOI list is not a list or is empty
    :raises ValueError: if no valid DOIs are found
    :return: list of cleaned-up DOIs
    :rtype: list[str]
    """
    if not doi_list or not isinstance(doi_list, list):
        raise ValueError(make_error("doi_list_format"))

    clean_doi_list = set()
    for putative_doi in doi_list:
        if putative_doi:
            clean_doi = str(putative_doi).strip()
            if clean_doi:
                clean_doi_list.add(clean_doi)

    if not clean_doi_list:
        raise ValueError(make_error("no_valid_dois"))

    return list(clean_doi_list)


def doi_to_file_name(doi: str) -> str:
    """Create an OS-friendly DOI string to use as a file name.
    Inspired by https://github.com/django/django/blob/main/django/utils/text.py

    :param doi: the doi
    :type doi: str
    :return: appropriate file name for the doi
    :rtype: str
    """
    f_name = (
        unicodedata.normalize("NFKD", doi).encode("ascii", "ignore").decode("ascii")
    )
    f_name = re.sub(r"[^\w\s\.\-]", "_", f_name)
    return re.sub(r"[-_\s]+", "_", f_name)


def full_path(file_path: Union[Path, str]) -> Path:
    """Generate the full path for a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string or Path object
    :return: full path
    :rtype: Path
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    cwd = Path.cwd()
    path_including_cwd = os.path.join(cwd, file_path)

    return Path.resolve(Path(path_including_cwd))


def dir_scanner(
    dir_path: Union[Path, str], conditions: Optional[list[Callable]] = None
) -> list[str]:
    """Scan a directory and return the paths of files that meet the conditions.
    If no conditions are given, returns all files except `.DS_Store`.

    :param dir_path: path to directory
    :type dir_path: str or Path object
    :param conditions: list of conditions that must evaluate to true
    :type conditions: list of functions
    :return file_list: list of full paths meeting the criteria
    :rtype file_list: list of strings
    """
    if not os.path.isabs(dir_path):
        # assume we need to add the standard full path pieces
        dir_path = full_path(dir_path)

    if os.path.isfile(dir_path):
        dir_path = os.path.dirname(dir_path)

    if not conditions:
        conditions = []

    file_list = []
    for f in os.listdir(dir_path):
        if f == ".DS_Store":
            continue
        if not os.path.isfile(os.path.join(dir_path, f)):
            continue

        meets_conditions = True
        for condition in conditions:
            if not condition(f):
                meets_conditions = False
                break
        if not meets_conditions:
            continue
        file_list.append(os.path.join(dir_path, f))

    return file_list


def read_json_file(file_path: Union[Path, str]) -> dict[str, Union[str, list, dict]]:
    """Read in JSON from a stored data file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string or Path object
    :return: parsed JSON data
    :rtype: dict
    """
    with open(full_path(file_path), encoding="utf-8") as fh:
        return json.load(fh)


def read_text_file(file_path: Union[Path, str]) -> list[str]:
    """Read in text from a stored data file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string or Path object
    :return: lines in the file with endings trimmed
    :rtype: list
    """
    with open(full_path(file_path)) as fh:
        return [line.rstrip() for line in fh]


def write_to_file(file_path: Union[Path, str], lines: Union[list, dict, str]):
    """Write a list of lines of text to a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string or Path object
    :param lines: content to be written to the file
    :type lines: list / dict / str
    """
    is_data_struct = False
    if isinstance(lines, dict):
        is_data_struct = True
    elif isinstance(lines, list):
        for line in lines:
            if isinstance(line, (list, dict)):
                is_data_struct = True
                break

    with open(full_path(file_path), "w", encoding="utf-8") as fh:
        if is_data_struct is True:
            # dump as JSON
            json.dump(lines, fh, indent=2, sort_keys=True)
        elif isinstance(lines, list):
            for line in lines:
                fh.write(str(line) + "\n")
        else:
            fh.write(str(lines))
    assert fh.closed


def write_bytes_to_file(file_path: Union[Path, str], file_bytes: bytes):
    """Write bytes to a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string or Path object
    :param file_bytes: bytes to be written to the file
    :type file_bytes: bytes
    """
    p = full_path(file_path)
    p.write_bytes(file_bytes)
