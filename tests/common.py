import json
import os.path
from pathlib import Path
from typing import Union

import _pytest.capture
import pytest

from credit_engine.parsers import doi
from credit_engine.util import dir_scanner


def check_stdout_for_errs(
    capsys: _pytest.capture.CaptureFixture,
    error_list: list[str],
):
    readouterr = capsys.readouterr()
    out_errors = readouterr.out.split("\n")
    for error in error_list:
        assert error in out_errors


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
    assert Path.exists(path_to_file) and Path.is_file(path_to_file)

    suffix = path_to_file.suffix
    content = None

    if suffix == ".xml":
        content = path_to_file.read_bytes()
    elif suffix == ".json":
        with Path.open(path_to_file) as fh:
            content = json.load(fh)
    elif suffix == ".txt":
        content = path_to_file.read_text()
    else:
        raise ValueError(f"Could not parse file based on suffix: {suffix}")

    # if content != expected:
    #     print(content)
    #     print({"expected": expected})
    assert content == expected


def run_retrieve_doi_list(
    capsys: _pytest.capture.CaptureFixture,
    default_dir: Path,
    param: dict,
    source: str,
    tmp_path: Path,
    format_list: list[str],
):
    """Retrieve and check a list of DOIs

    :param capsys: pytest stdout/stderr capture
    :type capsys: _type_
    :param default_dir: default directory for the data source
    :type default_dir: Path
    :param param: input parameters
    :type param: dict
    :param source: data source (e.g. 'crossref', 'datacite')
    :type source: str
    :param tmp_path: pytest temporary directory
    :type tmp_path: Path
    :param format_list: list of formats
    :type format_list: list[str]
    """

    file_list = []
    if "save_files" in param:
        save_dir = None
        save_files = param["save_files"]
        if "save_dir" in param:
            if param["save_dir"] == "tmp_path":
                save_dir = tmp_path / "specified_path"
                # ensure the save dir exists
                Path.mkdir(save_dir, exist_ok=True, parents=True)
            else:
                save_dir = param["save_dir"]

        else:
            Path.mkdir(default_dir, exist_ok=True, parents=True)

        retrieval_results = doi.retrieve_doi_list(
            param["input"], save_files, save_dir, source, format_list
        )

        assert retrieval_results["data"] == param["output"]["data"]

        if save_dir is None:
            save_dir = default_dir
            assert Path.exists(save_dir)

        # interpolate the path to the save directory
        file_list = [os.path.join(save_dir, doi) for doi in param["file_list"]]
        if save_dir != "/does/not/exist":
            assert set(dir_scanner(save_dir)) == set(file_list)
            if "files" in retrieval_results:
                # ensure file contents are as expected
                for f in retrieval_results["files"]:
                    for fmt in format_list:
                        run_file_contents_check(
                            retrieval_results["files"][f][fmt],
                            retrieval_results["data"][f][fmt],
                        )
        else:
            with pytest.raises(FileNotFoundError, match=r"No such file or directory"):
                dir_scanner(save_dir)
            assert retrieval_results["files"] == {}
    else:
        assert doi.retrieve_doi_list(param["input"], source=source) == param["output"]
        assert dir_scanner(tmp_path) == []

    if "errors" in param:
        check_stdout_for_errs(capsys, param["errors"])
