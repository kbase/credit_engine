import os
import json


def full_path(file_path: str) -> str:
    """Generate the full path for a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: str
    :return: full path
    :rtype: str
    """
    return os.path.join(os.getcwd(), file_path)


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


def write_to_file(file_path: str, lines: list):
    """Write a list of lines of text to a file.

    :param file_path: path relative to the credit_engine repo
    :type file_path: string
    :param lines: list containing things to be written to the file
    :type lines: list
    """
    with open(full_path(file_path), "w") as fh:
        fh.write(str(lines) + "\n")
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
