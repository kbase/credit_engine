import pytest

import credit_engine.parsers.doi as doi
from credit_engine.parsers import crossref
from credit_engine.parsers.crossref import DEFAULT_EMAIL, get_endpoint, retrieve_doi

from .common import run_retrieve_doi_list
from .conftest import (
    CLEAN_DOI_LIST_DATA,
    DOI_DATA,
    QUOTED_DOI,
    RETRIEVE_DOI_LIST_TEST_DATA,
    SAMPLE_DOI,
    SAMPLE_EMAIL,
)

GET_ENDPOINT_DATA = [
    pytest.param(
        [], f"https://api.crossref.org/works/{QUOTED_DOI}", id="default_format"
    ),
    pytest.param(["JSON"], f"https://api.crossref.org/works/{QUOTED_DOI}", id="json"),
    pytest.param(
        ["JSON", SAMPLE_EMAIL],
        f"https://api.crossref.org/works/{QUOTED_DOI}",
        id="json_with_email",
    ),
    pytest.param(
        ["UnixSd"],
        f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={QUOTED_DOI}",
        id="unixsd",
    ),
    pytest.param(
        ["UNIXSD", ""],
        f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={QUOTED_DOI}",
        id="unixsd_with_empty_email",
    ),
    pytest.param(
        ["UNIXSD", SAMPLE_EMAIL],
        f"https://doi.crossref.org/servlet/query?pid={SAMPLE_EMAIL}&format=unixsd&id={QUOTED_DOI}",
        id="unixsd_with_email",
    ),
    pytest.param(
        ["unixref"],
        f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixref&id={QUOTED_DOI}",
        id="unixref",
    ),
    pytest.param(
        ["UNIXref", SAMPLE_EMAIL],
        f"https://doi.crossref.org/servlet/query?pid={SAMPLE_EMAIL}&format=unixref&id={QUOTED_DOI}",
        id="unixref_with_email",
    ),
]


@pytest.mark.parametrize("test_input,expected", GET_ENDPOINT_DATA)
def test_get_endpoint_ok(test_input, expected):
    assert get_endpoint(SAMPLE_DOI, *test_input) == expected


def test_get_endpoint_fail():

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint()

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint("")

    with pytest.raises(ValueError, match=r"Invalid output format: XML"):
        get_endpoint("some_doi_here", "XML")


def test_retrieve_doi_ok(mock_response):
    assert retrieve_doi("VALID_DOI").json() == DOI_DATA["VALID_DOI"]


def test_retrieve_doi_fail(mock_response):
    with pytest.raises(
        ValueError, match="Request for NOT_FOUND failed with status code 404"
    ):
        retrieve_doi("NOT_FOUND")


@pytest.mark.parametrize("param", RETRIEVE_DOI_LIST_TEST_DATA)
def test_retrieve_doi_list(param, mock_response, tmp_path, capsys, monkeypatch):
    default_dir = tmp_path / "default_dir"
    monkeypatch.setattr(crossref, "SAMPLE_DATA_DIR", default_dir)

    run_retrieve_doi_list(
        capsys=capsys,
        default_dir=default_dir,
        param=param,
        source="crossref",
        tmp_path=tmp_path,
    )


@pytest.mark.parametrize("param", CLEAN_DOI_LIST_DATA)
def test_retrieve_doi_list_fail(param, mock_response):
    # only run tests where we know the test fails
    if "output" not in param:
        with pytest.raises(ValueError, match=param["error"]):
            doi.retrieve_doi_list(param["input"], source="crossref")
