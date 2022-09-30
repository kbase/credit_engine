import pytest

import credit_engine.constants as CE
import credit_engine.parsers.datacite as datacite
import credit_engine.parsers.doi as doi
from credit_engine.parsers.datacite import get_endpoint, retrieve_doi

from .common import check_stdout_for_errs
from .conftest import (
    A_VALID_DOI,
    NOT_FOUND,
    QUOTED_DOI,
    SAMPLE_DOI,
    generate_response_for_doi,
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
    assert retrieve_doi(A_VALID_DOI) == {
        CE.JSON: generate_response_for_doi(CE.DATACITE, A_VALID_DOI, CE.JSON)
    }


def test_retrieve_doi_ok_format_list(_mock_response):
    assert retrieve_doi(A_VALID_DOI, [CE.JSON, CE.XML]) == {
        CE.JSON: generate_response_for_doi(CE.DATACITE, A_VALID_DOI, CE.JSON),
        CE.XML: generate_response_for_doi(CE.DATACITE, A_VALID_DOI, CE.XML),
    }


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
