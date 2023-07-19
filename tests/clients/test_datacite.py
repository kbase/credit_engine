import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.datacite import get_endpoint, retrieve_doi
from tests.common import check_stdout_for_errs
from tests.conftest import (
    GET_ENDPOINT_FAIL_DATA,
    INVALID_JSON,
    INVALID_XML,
    NO_XML_NODE,
    NOT_FOUND_DOI_A,
    QUOTED_DOI,
    SAMPLE_DOI,
    VALID_DC_DOI_A,
    generate_response_for_doi,
)

GET_ENDPOINT_DATA = [
    pytest.param(
        {
            "input": [SAMPLE_DOI],
            "expected": f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true",
        },
        id="valid_input",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, None],
            "expected": f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true",
        },
        id="fmt_None",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.XML],
            "expected": f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true",
        },
        id="fmt_xml",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.JSON],
            "expected": f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true",
        },
        id="fmt_json",
    ),
]


@pytest.mark.parametrize("param", GET_ENDPOINT_DATA + GET_ENDPOINT_FAIL_DATA)
def test_get_endpoint(param):
    if "expected" in param:
        assert get_endpoint(*param["input"]) == param["expected"]
    else:
        with pytest.raises(ValueError, match=param["error"]):
            get_endpoint(*param["input"])  # type: ignore


fmt_list = [CE.JSON, CE.XML]
RETRIEVE_DOI_TEST_DATA = [
    pytest.param(
        {
            "input": [VALID_DC_DOI_A],
            "expected": {
                CE.JSON: generate_response_for_doi(CE.DATACITE, VALID_DC_DOI_A, CE.JSON)
            },
        },
        id="ok_default_format",
    ),
    pytest.param(
        {
            "input": [VALID_DC_DOI_A, fmt_list],
            "expected": {
                fmt: generate_response_for_doi(CE.DATACITE, VALID_DC_DOI_A, fmt)
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
    pytest.param(
        {
            "input": [NO_XML_NODE, fmt_list],
            "expected": {
                CE.JSON: {"this": "that"},
                CE.XML: None,
            },
            "stdout": [f"Error decoding XML for {NO_XML_NODE}: XML node not found"],
        },
        id="fail_no_xml_node",
    ),
    pytest.param(
        {
            "input": [INVALID_XML, [CE.XML]],
            "expected": {CE.XML: None},
            "stdout": [
                f"Error base64 decoding XML for {INVALID_XML}: Incorrect padding"
            ],
        },
        id="fail_invalid_xml",
    ),
    pytest.param(
        {
            "input": [INVALID_XML, fmt_list],
            "expected": {
                CE.JSON: {"data": {"attributes": {"xml": "abcdefghijklmopqrst"}}},
                CE.XML: None,
            },
            "stdout": [
                f"Error base64 decoding XML for {INVALID_XML}: Incorrect padding"
            ],
        },
        id="valid_json_invalid_xml",
    ),
]


@pytest.mark.parametrize("param", RETRIEVE_DOI_TEST_DATA)
def test_retrieve_doi(param, _mock_response, capsys):
    assert retrieve_doi(*param["input"]) == param["expected"]
    if "output" in param:
        check_stdout_for_errs(capsys, param["output"])
