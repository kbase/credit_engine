"""General utility functions."""

import json
import os
import re
import unicodedata
from collections.abc import Callable
from pathlib import Path

from pydantic import (
    DirectoryPath,
    FilePath,
    StrictBytes,
    StrictStr,
    constr,
    validate_arguments,
)

import credit_engine.constants as CE  # noqa: N812
from credit_engine.errors import make_error


@validate_arguments
def make_safe_file_name(doi: str) -> str:
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


@validate_arguments
def full_path(file_path: Path | str) -> Path:
    """Generate the full path for a file or directory.

    :param file_path: path, either absolute or relative to the credit_engine repo
    :type file_path: string or Path object
    :return: full path
    :rtype: Path
    """
    if isinstance(file_path, str):
        if not len(file_path.strip()):
            raise ValueError("a file path must be provided")
        file_path = Path(file_path)

    cwd = Path.cwd()
    path_including_cwd = os.path.join(cwd, file_path)

    return Path.resolve(Path(path_including_cwd))


@validate_arguments
def save_data_to_file(
    file_name: constr(strip_whitespace=True, min_length=1),  # type: ignore
    save_dir: DirectoryPath | str,
    suffix: str,
    data: bytes | str | list | dict | None,
) -> Path | None:
    """Save data to a file, specifying file name, dir, and extension.

    :param file_name: file base name, no extension
    :type file_name: str
    :param save_dir: directory in which to save the file
    :type save_dir: Path | str
    :param suffix: file extension
    :type suffix: str
    :param data: data to be saved
    :type data: bytes | str | list | dict | None
    :return: file path if successful, None otherwise
    :rtype: Path | None
    """
    # ensure we don't have an extra full stop
    if suffix.startswith("."):
        suffix = suffix[1:]

    out_file = Path(save_dir).joinpath(f"{make_safe_file_name(file_name)}.{suffix}")

    return save_data_to_file_full_path(out_file, data)


@validate_arguments
def save_data_to_file_full_path(
    file_path: Path | str, data: bytes | str | list | dict | None
) -> Path | None:
    """Save data to a file, specifying the full path and file name.

    :param file_path: full file path
    :type file_path: Path | str
    :param data: data to be saved
    :type data: bytes | str | list | dict | None
    :return: file path if successful, None otherwise
    :rtype: Path | None
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if data is None:
        print(f"{file_path}: no data to print")
        return None

    try:
        if isinstance(data, bytes):
            write_bytes_to_file(file_path, data)
        else:
            write_to_file(file_path, data)
        return file_path
    except OSError as e:
        print(e)
    # includes JSON encoding errors
    except Exception as e:
        print(type(Exception))
        print(e)

    return None


@validate_arguments
def read_json_file(file_path: FilePath | str) -> dict[str, str | list | dict] | list:
    """Read in JSON from a stored data file.

    :param file_path: path, either absolute or relative to the credit_engine repo
    :type file_path: string or Path object
    :return: parsed JSON data
    :rtype: dict
    """
    with open(full_path(file_path), encoding="utf-8") as fh:
        return json.load(fh)


@validate_arguments
def read_text_file(file_path: FilePath | str) -> list[str]:
    """Read in text from a stored data file.

    :param file_path: path, either absolute or relative to the credit_engine repo. N.b. an empty string is interpreted as '.'.
    :type file_path: string or Path object
    :return: lines in the file with endings trimmed
    :rtype: list[str]
    """
    with open(full_path(file_path)) as fh:
        return [line.strip() for line in fh]


@validate_arguments
def read_unique_lines(file_path: FilePath | str) -> set[str]:
    """Retrieve all unique, non-blank lines from a file.

    :param file_path: path, either absolute or relative to the credit_engine repo. N.b. an empty string is interpreted as '.'.
    :type file_path: Union[Path, str]
    :return: all unique, non-blank lines in the file
    :rtype: set[str]
    """
    all_lines = read_text_file(file_path)
    output = {line for line in all_lines if line}
    if not output:
        raise ValueError(f"No content found in {file_path}")
    return output


@validate_arguments
def write_to_file(file_path: Path | str, lines: list | dict | str):
    """Write a list of lines of text to a file.

    :param file_path: path, either absolute or relative to the credit_engine repo. N.b. an empty string is interpreted as '.'.
    :type file_path: string or Path object
    :param lines: content to be written to the file
    :type lines: list / dict / str
    """
    is_data_struct = False
    if isinstance(lines, dict):
        is_data_struct = True
    elif isinstance(lines, list):
        for line in lines:
            if isinstance(line, list | dict):
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
    if not fh.closed:
        fh.close()


@validate_arguments
def write_bytes_to_file(file_path: Path | str, file_bytes: bytes):
    """Write bytes to a file.

    :param file_path: path, either absolute or relative to the credit_engine repo. N.b. an empty string is interpreted as '.'.
    :type file_path: string or Path object
    :param file_bytes: bytes to be written to the file
    :type file_bytes: bytes
    """
    p = full_path(file_path)
    p.write_bytes(file_bytes)


@validate_arguments
def fix_line_endings(content: StrictStr | StrictBytes | None) -> str | bytes | None:
    """Ensure that all line endings are the same.

    :param content: text with line endings to be normalized
    :type content: Optional[str | bytes]
    :return: text with normalized line endings
    :rtype: Optional[str | bytes]
    """
    if content is None:
        return None

    if isinstance(content, bytes):
        return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

    return content.replace("\r\n", "\n").replace("\r", "\n")


@validate_arguments
def get_extension(fmt: CE.OutputFormat | str) -> str:
    """Get the appropriate file extension for saving data.

    :param fmt: format of data to be saved
    :type fmt: CE.OutputFormat | str
    :raises ValueError: if fmt is not a valid OutputFormat
    :return: file extension
    :rtype: str
    """
    if isinstance(fmt, CE.OutputFormat):
        output_format = fmt
    else:
        try:
            output_format = CE.OutputFormat[fmt.upper()]
        except KeyError:
            raise ValueError(
                make_error(
                    "invalid_param",
                    {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: fmt},
                )
            ) from KeyError

    if output_format.value in CE.EXT:
        return CE.EXT[output_format.value]

    raise ValueError(
        make_error(
            "invalid_param",
            {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: repr(output_format)},
        )
    )


@validate_arguments
def dir_scanner(
    dir_path: DirectoryPath | str, conditions: list[Callable] | None = None
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
