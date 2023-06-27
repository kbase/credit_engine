import pytest

import credit_engine.constants as CE
from credit_engine.clients.osti import get_endpoint, retrieve_doi
from tests.common import check_stdout_for_errs
from tests.conftest import (
    GET_ENDPOINT_FAIL_DATA,
    INVALID_JSON,
    NOT_FOUND,
    QUOTED_DOI,
    SAMPLE_DOI,
    VALID_DOI_A,
    generate_response_for_doi,
)

GET_ENDPOINT_DATA = [
    pytest.param(
        {
            "input": [SAMPLE_DOI],
            "expected": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
        },
        id="valid_input",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, None],
            "expected": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
        },
        id="fmt_None",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, CE.JSON],
            "expected": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
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
            "input": [VALID_DOI_A],
            "expected": {
                CE.JSON: generate_response_for_doi(CE.OSTI, VALID_DOI_A, CE.JSON)
            },
        },
        id="ok_default_format",
    ),
    pytest.param(
        {
            "input": [VALID_DOI_A, fmt_list],
            "expected": {
                fmt: generate_response_for_doi(CE.OSTI, VALID_DOI_A, fmt)
                for fmt in fmt_list
            },
        },
        id="ok_fmt_list",
    ),
    pytest.param(
        {
            "input": [NOT_FOUND],
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {NOT_FOUND} {CE.JSON} failed with status code 404"
            ],
        },
        id="fail_default_format",
    ),
    pytest.param(
        {
            "input": [NOT_FOUND, fmt_list],
            "expected": {fmt: None for fmt in fmt_list},
            "stdout": [
                f"Request for {NOT_FOUND} {fmt} failed with status code 404"
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
    # TODO: invalid xml test
]


@pytest.mark.parametrize("param", RETRIEVE_DOI_TEST_DATA)
def test_retrieve_doi(param, _mock_response, capsys):
    assert retrieve_doi(*param["input"]) == param["expected"]
    if "output" in param:
        check_stdout_for_errs(capsys, param["output"])
