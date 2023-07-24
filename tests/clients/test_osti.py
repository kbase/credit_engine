import re

import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.osti import ClientArgs, get_endpoint, retrieve_doi
from tests.common import check_stdout_for_errs
from tests.conftest import (
    GET_ENDPOINT_ERRORS,
    GET_ENDPOINT_ONE_ERROR,
    INVALID_JSON,
    NOT_FOUND_DOI_A,
    QUOTED_DOI,
    SAMPLE_DOI,
    VALID_DC_DOI_A,
    generate_response_for_doi,
)

GET_ENDPOINT_TEST_DATA = [
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI},
            "expected_url": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {SAMPLE_DOI} {CE.JSON} failed with status code 404"
            ],
        },
        id="valid_input",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": CE.OutputFormat.JSON},
            "expected_url": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {SAMPLE_DOI} {CE.JSON} failed with status code 404"
            ],
        },
        id="fmt_json",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": CE.OutputFormat.JSON},
            "expected_url": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {SAMPLE_DOI} {CE.JSON} failed with status code 404"
            ],
        },
        id="fmt_output_format_json",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": CE.OutputFormat.JSON},
            "expected_url": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {SAMPLE_DOI} {CE.JSON} failed with status code 404"
            ],
        },
        id="fmt_str_lc",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": CE.OutputFormat.XML},
            "expected_url": f"https://www.osti.gov/api/v1/records?doi={QUOTED_DOI}",
        },
        id="fmt_valid_output_format",
    ),
]


@pytest.mark.parametrize("param", GET_ENDPOINT_TEST_DATA)
def test_get_endpoint(param):
    client_args = ClientArgs(source=CE.OSTI, **param["input"])
    if "expected_url" in param:
        assert get_endpoint(doi=param["input"]["doi"]) == param["expected_url"]
    else:
        n_errors = len(param["error"])
        error_title = (
            str(n_errors) + GET_ENDPOINT_ONE_ERROR
            if n_errors == 1
            else GET_ENDPOINT_ERRORS
        )
        error_re = re.escape(error_title + "".join(param["error"]))
        with pytest.raises(ValueError, match=error_re):
            get_endpoint(doi=param["input"]["doi"])  # type: ignore


RETRIEVE_DOI_TEST_DATA = [
    pytest.param(
        {
            "input": {"doi": VALID_DC_DOI_A},
            "expected": {
                CE.JSON: generate_response_for_doi(CE.OSTI, VALID_DC_DOI_A, CE.JSON)
            },
        },
        id="ok_default_format",
    ),
    pytest.param(
        {
            "input": {"doi": VALID_DC_DOI_A, "output_formats": {CE.OutputFormat.JSON}},
            "expected": {
                "json": generate_response_for_doi(CE.OSTI, VALID_DC_DOI_A, CE.JSON)
            },
        },
        id="ok_fmt_json",
    ),
    pytest.param(
        {
            "input": {"doi": NOT_FOUND_DOI_A},
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {NOT_FOUND_DOI_A} {CE.JSON} failed with status code 404"
            ],
        },
        id="err_default_format",
    ),
    pytest.param(
        {
            "input": {"doi": NOT_FOUND_DOI_A, "output_formats": {CE.OutputFormat.JSON}},
            "expected": {
                "json": generate_response_for_doi(CE.OSTI, NOT_FOUND_DOI_A, CE.JSON)
            },
        },
        id="err_fmt_json",
    ),
    pytest.param(
        {
            "input": {"doi": INVALID_JSON, "output_formats": {CE.JSON}},
            "expected": {CE.JSON: None},
            "stdout": [
                f"Error decoding JSON for {INVALID_JSON}: Expecting ',' delimiter:"
                " line 1 column 16 (char 15)"
            ],
        },
        id="fail_invalid_json",
    ),
]


@pytest.mark.usefixtures("_mock_response")
@pytest.mark.parametrize("param", RETRIEVE_DOI_TEST_DATA)
def test_retrieve_doi(param, capsys):
    client_args = ClientArgs(source=CE.OSTI, **param["input"])

    if "error" in param:
        with pytest.raises(ValueError, match=param["error"]):
            retrieve_doi(client_args, param["input"]["doi"])
        return

    assert retrieve_doi(client_args, param["input"]["doi"]) == param["expected"]
    if "output" in param:
        check_stdout_for_errs(capsys, param["output"])
