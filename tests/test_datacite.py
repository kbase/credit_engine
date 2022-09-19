import pytest

import credit_engine.parsers.datacite as datacite
import credit_engine.parsers.doi as doi
from credit_engine.parsers.datacite import get_endpoint, retrieve_doi

from .common import check_stdout_for_errs, run_retrieve_doi_list
from .conftest import (
    CLEAN_DOI_LIST_DATA,
    DOI_DATA,
    NOT_FOUND,
    QUOTED_DOI,
    RETRIEVE_DOI_LIST_TEST_DATA,
    SAMPLE_DOI,
    VALID_DOI,
)


def test_get_endpoint_ok():
    expected = f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true"
    assert get_endpoint(SAMPLE_DOI) == expected


def test_get_endpoint_fail():
    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint()

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint("")


def test_retrieve_doi_ok_default_format(_mock_response):
    assert retrieve_doi(VALID_DOI) == {"json": DOI_DATA[VALID_DOI]}


def test_retrieve_doi_ok_format_list(_mock_response):
    # TODO!
    pass
    # assert retrieve_doi(VALID_DOI, ["json", "xml"]) == {"json": ..., "xml": ...}


def test_retrieve_doi_fail_default_format(_mock_response, capsys):
    assert retrieve_doi(NOT_FOUND) == {"json": None}
    check_stdout_for_errs(
        capsys, ["Request for NOT_FOUND json failed with status code 404"]
    )


def test_retrieve_doi_fail_format_list(_mock_response, capsys):
    fmt_list = ["json", "xml"]
    assert retrieve_doi(NOT_FOUND, fmt_list) == {"json": None, "xml": None}
    check_stdout_for_errs(
        capsys,
        [
            f"Request for NOT_FOUND {fmt} failed with status code 404"
            for fmt in fmt_list
        ],
    )


@pytest.mark.parametrize("param", RETRIEVE_DOI_LIST_TEST_DATA)
def test_retrieve_doi_list(param, _mock_response, tmp_path, capsys, monkeypatch):
    default_dir = tmp_path / "default_dir"
    monkeypatch.setattr(datacite, "SAMPLE_DATA_DIR", default_dir)

    run_retrieve_doi_list(
        capsys=capsys,
        default_dir=default_dir,
        param=param,
        source="datacite",
        tmp_path=tmp_path,
    )


@pytest.mark.parametrize("param", CLEAN_DOI_LIST_DATA)
def test_retrieve_doi_list_fail(param, _mock_response):
    # only run tests where we know the test fails
    if "output" not in param:
        with pytest.raises(ValueError, match=param["error"]):
            doi.retrieve_doi_list(param["input"], source="datacite")
