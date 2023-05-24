import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Callable, Optional, Union

from pydantic import validate_arguments

import credit_engine.constants as CE


@validate_arguments
def clean_doi_list(doi_list: Optional[list[str]]) -> list[str]:
    """Clean up a list of DOIs.

    Dedupe and remove blanks.

    :param doi_list: list of putative DOIs
    :type doi_list: list[str]
    :raises ValueError: if DOI list is not a list
    :return: list (possibly empty) of cleaned-up DOIs
    :rtype: list[str]
    """
    clean_doi_list = []
    if not doi_list:
        return clean_doi_list
    for putative_doi in set(doi_list):
        if putative_doi:
            clean_doi = putative_doi.strip()
            if clean_doi:
                clean_doi_list.append(clean_doi)

    return clean_doi_list


def doi_to_file_name(doi: str) -> str:
    """Create an OS-friendly string to use as a file name.
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

    :param file_path: path, either absolute or relative to the credit_engine repo
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


@validate_arguments
def save_data_to_file(
    file_name: CE.TrimmedString,
    save_dir: Union[Path, str],
    suffix: str,
    data: Union[bytes, str, list, dict],
) -> Optional[Path]:
    # ensure we don't have an extra full stop
    if suffix.startswith("."):
        suffix = suffix[1:]

    out_file = Path(save_dir).joinpath(f"{doi_to_file_name(file_name)}.{suffix}")
    try:
        if isinstance(data, bytes):
            write_bytes_to_file(out_file, data)
        else:
            write_to_file(out_file, data)
        return out_file
    except OSError as e:
        print(e)
    # includes JSON encoding errors
    except Exception as e:
        print(type(Exception))
        print(e)

    return None


def read_json_file(file_path: Union[Path, str]) -> dict[str, Union[str, list, dict]]:
    """Read in JSON from a stored data file.

    :param file_path: path, either absolute or relative to the credit_engine repo
    :type file_path: string or Path object
    :return: parsed JSON data
    :rtype: dict
    """
    with open(full_path(file_path), encoding="utf-8") as fh:
        return json.load(fh)


def read_text_file(file_path: Union[Path, str]) -> list[str]:
    """Read in text from a stored data file.

    :param file_path: path, either absolute or relative to the credit_engine repo
    :type file_path: string or Path object
    :return: lines in the file with endings trimmed
    :rtype: list
    """
    with open(full_path(file_path)) as fh:
        return [line.strip() for line in fh]


def read_unique_lines(file_path: Union[Path, str]) -> list[str]:
    """Retrieve all unique, non-blank lines from a file.

    :param file_path: path, either absolute or relative to the credit_engine repo
    :type file_path: Union[Path, str]
    :return: _description_
    :rtype: list[str]
    """
    all_lines = read_text_file(file_path)
    return [line for line in list(set(all_lines)) if line]


def write_to_file(file_path: Union[Path, str], lines: Union[list, dict, str]):
    """Write a list of lines of text to a file.

    :param file_path: path, either absolute or relative to the credit_engine repo
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

    :param file_path: path, either absolute or relative to the credit_engine repo
    :type file_path: string or Path object
    :param file_bytes: bytes to be written to the file
    :type file_bytes: bytes
    """
    p = full_path(file_path)
    p.write_bytes(file_bytes)
