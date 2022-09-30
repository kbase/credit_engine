import pytest
import re

import credit_engine.constants as CE
from credit_engine.parsers.crossref import DEFAULT_EMAIL, get_endpoint, retrieve_doi

from tests.common import check_stdout_for_errs
from tests.conftest import (
    A_VALID_DOI,
    NOT_FOUND,
    INVALID_JSON,
    QUOTED_DOI,
    SAMPLE_DOI,
    SAMPLE_EMAIL,
    generate_response_for_doi,
)

GET_ENDPOINT_DATA = [
    pytest.param(
        None, f"https://api.crossref.org/works/{QUOTED_DOI}", id="no_extra_args"
    ),
    pytest.param(
        [], f"https://api.crossref.org/works/{QUOTED_DOI}", id="default_format"
    ),
    pytest.param(
        [None], f"https://api.crossref.org/works/{QUOTED_DOI}", id="list_of_none"
    ),
    pytest.param(
        [""],
        f"https://api.crossref.org/works/{QUOTED_DOI}",
        id="list_of_zero_length_str",
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
    if test_input is not None:
        assert get_endpoint(SAMPLE_DOI, *test_input) == expected
    else:
        assert get_endpoint(SAMPLE_DOI) == expected


def test_get_endpoint_fail_no_args():
    error_msg = re.escape(
        "1 validation error for GetEndpoint\ndoi\n  field required (type=value_error.missing)"
    )
    with pytest.raises(ValueError, match=error_msg):
        get_endpoint()  # type: ignore


def test_get_endpoint_fail_empty_args():
    error_msg = re.escape(
        "1 validation error for GetEndpoint\ndoi\n  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)"
    )
    with pytest.raises(ValueError, match=error_msg):
        get_endpoint("")  # type: ignore


def test_get_endpoint_fail_whitespace():
    error_msg = re.escape(
        "1 validation error for GetEndpoint\ndoi\n  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)"
    )
    with pytest.raises(ValueError, match=error_msg):
        get_endpoint("         \n\n   ")  # type: ignore


def test_endpoint_fail_invalid_format():
    with pytest.raises(ValueError, match=r"Invalid output format: XML"):
        get_endpoint("some_doi_here", "XML")  # type: ignore


def test_retrieve_doi_ok_empty_format(_mock_response):
    assert retrieve_doi(A_VALID_DOI) == {
        CE.JSON: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.JSON)
    }


def test_retrieve_doi_ok_format_list(_mock_response):
    assert retrieve_doi(A_VALID_DOI, [CE.UNIXREF, CE.UNIXSD]) == {
        CE.UNIXSD: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.UNIXSD),
        CE.UNIXREF: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.UNIXREF),
    }


def test_retrieve_doi_fail_default_format(_mock_response, capsys):
    assert retrieve_doi(NOT_FOUND) == {CE.JSON: None}
    check_stdout_for_errs(
        capsys, [f"Request for {NOT_FOUND} {CE.JSON} failed with status code 404"]
    )


def test_retrieve_doi_fail_format_list(_mock_response, capsys):
    fmt_list = ["unixref", "unixsd"]
    assert retrieve_doi(NOT_FOUND, fmt_list) == {CE.UNIXREF: None, CE.UNIXSD: None}
    check_stdout_for_errs(
        capsys,
        [
            f"Request for {NOT_FOUND} {fmt} failed with status code 404"
            for fmt in fmt_list
        ],
    )


def test_retrieve_doi_fail_invalid_json(_mock_response, capsys):
    fmt = CE.JSON
    assert retrieve_doi(INVALID_JSON, [fmt]) == {CE.JSON: None}
    check_stdout_for_errs(
        capsys,
        [
            f"Error decoding JSON for {INVALID_JSON}: Expecting ',' delimiter: line 1 column 16 (char 15)"
        ],
    )
