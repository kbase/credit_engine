import json
import os
from typing import Union


def full_path(file_path: str) -> str:
    """Generate the full path for a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: str
    :return: full path
    :rtype: str
    """
    return os.path.abspath(os.path.join(os.getcwd(), file_path))


def dir_scanner(dir_path: str, conditions: Union[list, None] = None) -> list[str]:
    """Create a generator that scans a directory and returns the paths of files that meeet the conditions.

    :param dir_path: path to directory
    :type dir_path: str
    :param conditions: list of conditions that must evaluate to true
    :type conditions: list of functions
    :return file_list: list of full paths meeting the criteria
    :rtype file_list: list of strings
    """
    if not dir_path.startswith("/"):
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
    with open(full_path(file_path)) as fh:
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
    with open(full_path(file_path), "w") as fh:
        if isinstance(lines, list):
            is_data_struct = False
            for line in lines:
                if isinstance(line, (list, dict)):
                    is_data_struct = True
                    break

            if is_data_struct:
                # dump as JSON
                fh.write(json.dumps(lines, indent=2, sort_keys=True))
            else:
                for line in lines:
                    fh.write(str(line) + "\n")

        elif isinstance(lines, dict):
            # dump as JSON
            fh.write(json.dumps(lines, indent=2, sort_keys=True))
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
    with open(full_path(file_path), "wb") as fh:
        fh.write(file_bytes)
        fh.close()
