import json
from pathlib import Path
import os
from typing import Union, Optional, List
from urllib.parse import quote
import unicodedata
import re


def encode_doi(doi: str) -> str:
    """Encodes any dodgy doi characters for use as an URL.
    See https://www.doi.org/doi_handbook/2_Numbering.html#2.5.2 for DOI encoding recs
    :param doi: the doi
    :type doi: str
    :return: encoded doi for URI usage
    :rtype: str
    """
    return quote(doi)


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
    f_name = re.sub(r"[^\w\s\.\-]", "_", f_name.lower())
    return re.sub(r"[-_\s]+", "_", f_name)


def full_path(file_path: Union[Path, str]) -> Path:
    """Generate the full path for a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: Path
    :return: full path
    :rtype: Path
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    cwd = Path.cwd()
    full_path = os.path.join(cwd, file_path)

    return Path.resolve(Path(full_path))


def dir_scanner(
    dir_path: Union[Path, str], conditions: Optional[list] = None
) -> List[str]:
    """Scan a directory and return the paths of files that meet the conditions.
    If no conditions are given, returns all files except `.DS_Store`.

    :param dir_path: path to directory
    :type dir_path: str
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


def read_json_file(file_path: str) -> dict:
    """Read in JSON from a stored data file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string
    :return: parsed JSON data
    :rtype: dict
    """
    with open(full_path(file_path), encoding="utf-8") as fh:
        return json.load(fh)


def read_text_file(file_path: str) -> list:
    """Read in text from a stored data file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string
    :return: lines in the file with endings trimmed
    :rtype: list
    """
    with open(full_path(file_path)) as fh:
        return [line.rstrip() for line in fh]


def write_to_file(file_path: str, lines: Union[list, dict, str]):
    """Write a list of lines of text to a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string
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
        fh.close()


def write_bytes_to_file(file_path: str, file_bytes: bytes):
    """Write bytes to a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string
    :param file_bytes: bytes to be written to the file
    :type file_bytes: bytes
    """
    p = full_path(file_path)
    p.write_bytes(file_bytes)
