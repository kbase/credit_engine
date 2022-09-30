import pytest

import credit_engine.constants as CE
import credit_engine.parsers.doi as doi
from credit_engine.parsers import crossref
from credit_engine.parsers.crossref import DEFAULT_EMAIL, get_endpoint, retrieve_doi

from .common import check_stdout_for_errs
from .conftest import (
    A_VALID_DOI,
    NOT_FOUND,
    QUOTED_DOI,
    SAMPLE_DOI,
    SAMPLE_EMAIL,
    generate_response_for_doi,
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


def test_retrieve_doi_ok_default_format(_mock_response):
    assert retrieve_doi(A_VALID_DOI) == {
        CE.JSON: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.JSON)
    }


def test_retrieve_doi_ok_format_list(_mock_response):
    assert retrieve_doi(A_VALID_DOI, [CE.UNIXREF, CE.UNIXSD]) == {
        CE.UNIXSD: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.UNIXSD),
        CE.UNIXREF: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.UNIXREF),
    }


def test_retrieve_doi_fail_default_format(_mock_response, capsys):
    assert retrieve_doi(NOT_FOUND) == {"json": None}
    check_stdout_for_errs(
        capsys, ["Request for NOT_FOUND json failed with status code 404"]
    )


def test_retrieve_doi_fail_format_list(_mock_response, capsys):
    fmt_list = ["unixref", "unixsd"]
    assert retrieve_doi(NOT_FOUND, fmt_list) == {"unixref": None, "unixsd": None}
    check_stdout_for_errs(
        capsys,
        [
            f"Request for NOT_FOUND {fmt} failed with status code 404"
            for fmt in fmt_list
        ],
    )
