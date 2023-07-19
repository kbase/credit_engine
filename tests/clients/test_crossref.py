import re

import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.crossref import check_doi_source, get_endpoint, retrieve_doi
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
    VALID_DC_DOI,
    VALID_XR_DOI,
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
            "input": [SAMPLE_DOI, CE.OutputFormat.JSON],
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_json",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.JSON, SAMPLE_EMAIL],
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_json_with_email",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.XML],
            "expected": f"https://doi.crossref.org/servlet/query?format=unixsd&id={QUOTED_DOI}&pid={QUOTED_DEFAULT_EMAIL}",
        },
        id="fmt_xml",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.XML, None],
            "expected": f"https://doi.crossref.org/servlet/query?format=unixsd&id={QUOTED_DOI}&pid={QUOTED_DEFAULT_EMAIL}",
        },
        id="fmt_xml_email_None",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.XML, ""],
            "error": re.escape(EMAIL_VALIDATION_ERROR),
        },
        id="fmt_xml_email_len_0",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.XML, SPACE_STR],
            "error": re.escape(EMAIL_VALIDATION_ERROR),
        },
        id="fmt_xml_email_whitespace",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.XML, "fake email address"],
            "error": re.escape(EMAIL_VALIDATION_ERROR),
        },
        id="fmt_xml_email_fake_email",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.OutputFormat.XML, SAMPLE_EMAIL],
            "expected": f"https://doi.crossref.org/servlet/query?format=unixsd&id={QUOTED_DOI}&pid={QUOTED_EMAIL}",
        },
        id="fmt_xml_with_email",
    ),
]


@pytest.mark.parametrize("param", GET_ENDPOINT_DATA + GET_ENDPOINT_FAIL_DATA)
def test_get_endpoint(param):
    if len(param["input"]) == 0:
        with pytest.raises(ValueError, match=param["error"]):
            get_endpoint()  # type: ignore
        return

    if "expected" in param:
        assert get_endpoint(*param["input"]) == param["expected"]
    else:
        with pytest.raises(ValueError, match=param["error"]):
            get_endpoint(*param["input"])  # type: ignore


fmt_list = [CE.JSON, CE.XML]
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


CHECK_DOI_SOURCE_TEST_DATA = [
    pytest.param(
        {
            "doi": VALID_DC_DOI,
            "expected": "datacite",
        },
        id="datacite",
    ),
    pytest.param(
        {
            "doi": VALID_XR_DOI,
            "expected": "crossref",
        },
        id="crossref",
    ),
    pytest.param(
        {
            "doi": NOT_FOUND_DOI_A,
            "expected": None,
        },
        id="not_found",
    ),
]


@pytest.mark.parametrize("param", CHECK_DOI_SOURCE_TEST_DATA)
def test_check_doi_source(param, _mock_response):
    """Test the DOI source function

    :param param: doi: the DOI to query; expected: expected result
    :type param: pytest.param
    :param _mock_response: mock requests.get function
    :type _mock_response: pytest mock
    """
    assert check_doi_source(param["doi"]) == param["expected"]
