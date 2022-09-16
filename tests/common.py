import os.path
from pathlib import Path

import pytest

from credit_engine.parsers import doi
from credit_engine.util import dir_scanner


def run_retrieve_doi_list(
    capsys,
    default_dir,
    param,
    source,
    tmp_path,
):

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
            param["input"], save_files, save_dir, source
        )

        assert retrieval_results["data"] == param["output"]["data"]

        if save_dir is None:
            save_dir = default_dir
            assert Path.exists(save_dir)

        # interpolate the path to the save directory
        file_list = [os.path.join(save_dir, doi) for doi in param["file_list"]]
        # TODO: add file contents check
        if save_dir != "/does/not/exist":
            assert set(dir_scanner(save_dir)) == set(file_list)
        else:
            with pytest.raises(FileNotFoundError, match=r"No such file or directory"):
                dir_scanner(save_dir)
            assert retrieval_results["files"] == {}
    else:
        assert doi.retrieve_doi_list(param["input"], source=source) == param["output"]
        assert dir_scanner(tmp_path) == []

    if "errors" in param:
        readouterr = capsys.readouterr()
        out_errors = readouterr.out.split("\n")
        for error in param["errors"]:
            assert error in out_errors
