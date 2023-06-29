import re

import pytest

import credit_engine.constants as CE
from credit_engine.clients.crossref import get_endpoint, retrieve_doi
from tests.common import check_stdout_for_errs
from tests.conftest import (
    GET_ENDPOINT_FAIL_DATA,
    INVALID_JSON,
    NOT_FOUND_DOI_A,
    QUOTED_DEFAULT_EMAIL,
    QUOTED_DOI,
    QUOTED_EMAIL,
    SAMPLE_DOI,
    SAMPLE_EMAIL,
    SPACE_STR,
    VALID_XR_DOI_A,
    generate_response_for_doi,
)

EMAIL_VALIDATION_ERROR = (
    "1 validation error for GetEndpoint\nemail_address\n"
    "  value is not a valid email address (type=value_error.email)"
)

GET_ENDPOINT_DATA = [
    pytest.param(
        {
            "input": [SAMPLE_DOI],
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="doi_only",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, None],
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_None",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "JSON"],
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_json",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "JSON", SAMPLE_EMAIL],
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_json_with_email",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UnixSd"],
            "expected": f"https://doi.crossref.org/servlet/query?id={QUOTED_DOI}&format={CE.UNIXSD}&pid={QUOTED_DEFAULT_EMAIL}",
        },
        id="fmt_unixsd",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UnixSd", None],
            "expected": f"https://doi.crossref.org/servlet/query?id={QUOTED_DOI}&format={CE.UNIXSD}&pid={QUOTED_DEFAULT_EMAIL}",
        },
        id="fmt_unixsd_email_None",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UNIXSD", ""],
            "error": re.escape(EMAIL_VALIDATION_ERROR),
        },
        id="fmt_unixsd_email_len_0",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UNIXSD", SPACE_STR],
            "error": re.escape(EMAIL_VALIDATION_ERROR),
        },
        id="fmt_unixsd_email_whitespace",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UNIXSD", "fake email address"],
            "error": re.escape(EMAIL_VALIDATION_ERROR),
        },
        id="fmt_unixsd_email_fake_email",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UNIXSD", SAMPLE_EMAIL],
            "expected": f"https://doi.crossref.org/servlet/query?id={QUOTED_DOI}&format={CE.UNIXSD}&pid={QUOTED_EMAIL}",
        },
        id="fmt_unixsd_with_email",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "Unixref"],
            "expected": f"https://doi.crossref.org/servlet/query?id={QUOTED_DOI}&format={CE.UNIXREF}&pid={QUOTED_DEFAULT_EMAIL}",
        },
        id="fmt_unixref",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "UNIXref", SAMPLE_EMAIL],
            "expected": f"https://doi.crossref.org/servlet/query?id={QUOTED_DOI}&format={CE.UNIXREF}&pid={QUOTED_EMAIL}",
        },
        id="fmt_unixref_with_email",
    ),
]


@pytest.mark.parametrize("param", GET_ENDPOINT_DATA + GET_ENDPOINT_FAIL_DATA)
def test_get_endpoint(param):
    if "expected" in param:
        assert get_endpoint(*param["input"]) == param["expected"]
    else:
        with pytest.raises(ValueError, match=param["error"]):
            get_endpoint(*param["input"])  # type: ignore


fmt_list = [CE.JSON, CE.UNIXREF, CE.UNIXSD]
RETRIEVE_DOI_TEST_DATA = [
    pytest.param(
        {
            "input": [VALID_XR_DOI_A],
            "expected": {
                CE.JSON: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_A, CE.JSON)
            },
        },
        id="ok_default_format",
    ),
    pytest.param(
        {
            "input": [VALID_XR_DOI_A, fmt_list],
            "expected": {
                fmt: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_A, fmt)
                for fmt in fmt_list
            },
        },
        id="ok_fmt_list",
    ),
    pytest.param(
        {
            "input": [NOT_FOUND_DOI_A],
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {NOT_FOUND_DOI_A} {CE.JSON} failed with status code 404"
            ],
        },
        id="fail_default_format",
    ),
    pytest.param(
        {
            "input": [NOT_FOUND_DOI_A, fmt_list],
            "expected": {fmt: None for fmt in fmt_list},
            "stdout": [
                f"Request for {NOT_FOUND_DOI_A} {fmt} failed with status code 404"
                for fmt in fmt_list
            ],
        },
        id="fail_fmt_list",
    ),
    pytest.param(
        {
            "input": [INVALID_JSON, [CE.JSON]],
            "expected": {CE.JSON: None},
            "stdout": [
                f"Error decoding JSON for {INVALID_JSON}: Expecting ',' delimiter:"
                " line 1 column 16 (char 15)"
            ],
        },
        id="fail_invalid_json",
    ),
]


@pytest.mark.parametrize("param", RETRIEVE_DOI_TEST_DATA)
def test_retrieve_doi(param, _mock_response, capsys):
    assert retrieve_doi(*param["input"]) == param["expected"]
    if "output" in param:
        check_stdout_for_errs(capsys, param["output"])
