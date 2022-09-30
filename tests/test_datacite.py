import pytest
import re
import credit_engine.constants as CE
from credit_engine.parsers.datacite import get_endpoint, retrieve_doi

from tests.common import check_stdout_for_errs
from tests.conftest import (
    A_VALID_DOI,
    NOT_FOUND,
    QUOTED_DOI,
    SAMPLE_DOI,
    INVALID_JSON,
    INVALID_XML,
    NO_XML_NODE,
    generate_response_for_doi,
)


def test_get_endpoint_ok():
    expected = f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true"
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
    assert retrieve_doi(NOT_FOUND) == {CE.JSON: None}
    check_stdout_for_errs(
        capsys, [f"Request for {NOT_FOUND} {CE.JSON} failed with status code 404"]
    )


def test_retrieve_doi_fail_format_list(_mock_response, capsys):
    fmt_list = [CE.JSON, CE.XML]
    assert retrieve_doi(NOT_FOUND, fmt_list) == {CE.JSON: None, CE.XML: None}
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


def test_retrieve_doi_fail_no_xml_node(_mock_response, capsys):
    fmt_list = [CE.JSON, CE.XML]
    assert retrieve_doi(NO_XML_NODE, fmt_list) == {
        CE.JSON: {"this": "that"},
        CE.XML: None,
    }
    check_stdout_for_errs(
        capsys,
        [f"Error decoding XML for {NO_XML_NODE}: XML node not found"],
    )


def test_retrieve_doi_fail_invalid_encoded_data(_mock_response, capsys):
    fmt_list = [CE.JSON, CE.XML]
    assert retrieve_doi(INVALID_XML, fmt_list) == {
        CE.JSON: {"data": {"attributes": {"xml": "abcdefghijklmopqrst"}}},
        CE.XML: None,
    }
    check_stdout_for_errs(
        capsys,
        [f"Error base64 decoding XML for {INVALID_XML}: Incorrect padding"],
    )
