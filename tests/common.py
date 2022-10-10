import json
import os.path
import re
from pathlib import Path
from typing import Pattern, Union

import _pytest.capture
import pytest

import credit_engine.constants as CE
from credit_engine.parsers import base
from credit_engine.util import dir_scanner

VERBOSE = False


def check_stdout_for_errs(
    capsys: _pytest.capture.CaptureFixture,
    error_list: list[str],
):
    readouterr = capsys.readouterr()
    out_errors = readouterr.out.split("\n")
    if VERBOSE:
        print({"STDOUT": out_errors})
        print(error_list)
    for error in error_list:
        assert error in out_errors


def check_stderr_for_errs(
    capsys: _pytest.capture.CaptureFixture,
    error_list: list[str],
):
    readouterr = capsys.readouterr()
    out_errors = readouterr.err.split("\n")
    if VERBOSE:
        print({"STDERR": out_errors})
        print(error_list)
    for error in error_list:
        assert error in out_errors


def check_for_errors(string_list, error_list):
    for error in error_list:
        if isinstance(error, Pattern):
            # error is a regular expression
            found_it = False
            for string in string_list:
                if re.search(error, string):
                    found_it = True
                    break
            assert found_it is True
        else:
            assert error in string_list


def run_file_contents_check(
    file_path: Union[Path, str], expected: Union[bytes, str, list, dict]
):
    """Assert that the contents of the file match the expected content.

    :param file_path: file to check
    :type file_path: Union[Path, str]
    :param expected: expected file contents
    :type expected: Union[bytes, str, list, dict]
    """
    path_to_file = Path(file_path)
    assert Path(path_to_file).exists() and Path(path_to_file).is_file()

    suffix = path_to_file.suffix
    content = None

    if suffix == f".{CE.XML}":
        content = path_to_file.read_bytes()
    elif suffix == f".{CE.JSON}":
        with Path.open(path_to_file) as fh:
            content = json.load(fh)
    elif suffix == ".txt":
        content = path_to_file.read_text()
    else:
        raise ValueError(f"Could not parse file based on suffix: {suffix}")

    assert content == expected


def run_retrieve_doi_list(
    param: dict,
    expected: dict,
    default_dir: Path,
    tmp_path: Path,
    capsys: _pytest.capture.CaptureFixture,
):
    """Retrieve and check a list of DOIs.

    :param param: input parameters
    :type param: dict
    :param expected: expected results
    :type expected: dict
    :param default_dir: default directory for the data source
    :type default_dir: Path
    :param tmp_path: temporary directory
    :type tmp_path: Path
    :param capsys: pytest stdout/stderr capture
    :type capsys: _type_
    """
    output_format_list = list(set(param["output_format_list"]))

    if "save_files" in param and param["save_files"]:
        save_dir = param["save_dir"] if "save_dir" in param else default_dir
        assert Path(save_dir).exists()
        # interpolate the path to the save directory
        file_list = [os.path.join(save_dir, doi) for doi in expected["file_list"]]

        retrieval_results = base.retrieve_doi_list(**param)
        # assert set(retrieval_results["data"].keys()) == set(expected["output"]["data"].keys())
        # for key in expected["output"]["data"]:
        #     if retrieval_results["data"][key] != expected["output"]["data"][key]:
        #         for subkey in retrieval_results["data"][key]:
        #             if retrieval_results["data"][key][subkey] != expected["output"]["data"][key][subkey]:
        #                 print("\n\n")
        #                 print({"mismatched results: " + key + ":" + subkey})
        #                 print({"got": retrieval_results["data"][key][subkey]})
        #                 print("\n")
        #                 print({"exp": expected["output"]["data"][key][subkey]})
        #                 print("\n\n")
        #     assert retrieval_results["data"][key] == expected["output"]["data"][key]

        assert retrieval_results["data"] == expected["output"]["data"]
        assert set(dir_scanner(save_dir)) == set(file_list)

        # ensure file contents are as expected
        assert "files" in retrieval_results
        for f in retrieval_results["files"]:
            for fmt in output_format_list:
                if retrieval_results["data"][f][fmt] is None:
                    assert retrieval_results["files"][f][fmt] is None
                else:
                    run_file_contents_check(
                        retrieval_results["files"][f][fmt],
                        retrieval_results["data"][f][fmt],
                    )
    else:
        retrieval_results = base.retrieve_doi_list(**param)
        assert retrieval_results == expected["output"]
        assert dir_scanner(tmp_path) == []

    if "errors" in expected:
        check_stdout_for_errs(capsys, expected["errors"])
