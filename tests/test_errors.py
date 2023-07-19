import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine import errors
from credit_engine.errors import ERROR_STRING

MAKE_ERROR_TEST_DATA = [
    pytest.param(
        {
            "input": [],
            "output": ERROR_STRING["generic"],
        },
        id="no_args",
    ),
    pytest.param(
        {
            "input": ["this error type does not exist"],
            "output": ERROR_STRING["generic"],
        },
        id="invalid_args",
    ),
    pytest.param(
        {
            "input": ["doi_list_format"],
            "output": ERROR_STRING["doi_list_format"],
        },
        id="zero_len_list",
    ),
    pytest.param(
        {
            "input": ["doi_list_format", {"this": "that"}],
            "output": ERROR_STRING["doi_list_format"],
        },
        id="zero_len_list_extra_args",
    ),
    pytest.param(
        {
            "input": ["no_valid_dois"],
            "output": ERROR_STRING["no_valid_dois"],
        },
        id="no_valid_dois",
    ),
    pytest.param(
        {
            "input": ["missing_required"],
            "output": ERROR_STRING["missing_required"],
        },
        id="missing_required_no_args",
    ),
    pytest.param(
        {
            "input": ["missing_required", ""],
            "output": ERROR_STRING["missing_required"],
        },
        id="missing_required_wrong_args_type",
    ),
    pytest.param(
        {"input": ["missing_required", {}], "output": ERROR_STRING["missing_required"]},
        id="missing_required_empty_args",
    ),
    pytest.param(
        {
            "input": ["missing_required", {"this": "that"}],
            "output": "Missing required argument: REQUIRED",
        },
        id="missing_required_invalid_args",
    ),
    pytest.param(
        {
            "input": ["missing_required", {"required": "koala"}],
            "output": "Missing required argument: koala",
        },
        id="missing_required_valid_args",
    ),
    pytest.param(
        {
            "input": ["invalid_param", {}],
            "output": ERROR_STRING["invalid_param"],
        },
        id="invalid_param_empty_args",
    ),
    pytest.param(
        {
            "input": ["invalid_param", {"this": "that"}],
            "output": 'Invalid parameter: "{"this": "that"}"',
        },
        id="invalid_param_no_param",
    ),
    pytest.param(
        {
            "input": ["invalid_param", {"param": "koala"}],
            "output": 'Invalid koala: "{"param": "koala"}"',
        },
        id="invalid_param_param_no_args",
    ),
    pytest.param(
        {
            "input": [
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, "format": "morse code"},
            ],
            "output": 'Invalid output format: "{"format": "morse code", "param": "output format"}"',
        },
        id="invalid_param_param_invalid_args",
    ),
    pytest.param(
        {
            "input": [
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: "elevator music"},
            ],
            "output": 'Invalid output format: "elevator music"',
        },
        id="invalid_param_valid_args",
    ),
    pytest.param(
        {"input": ["http_error"], "output": "HTTP request failed"},
        id="http_error_no_args",
    ),
    pytest.param(
        {"input": ["http_error", {}], "output": "HTTP request failed"},
        id="http_error_empty_args",
    ),
    pytest.param(
        {
            "input": ["http_error", {"doi": "my_fave_doi", "status_code": 301}],
            "output": "Request for my_fave_doi failed with status code 301",
        },
        id="http_error_all_args",
    ),
    pytest.param(
        {
            "input": ["http_error", {"status_code": 500}],
            "output": "Request for DOI failed with status code 500",
        },
        id="http_error_partial_args",
    ),
]


@pytest.mark.parametrize("param", MAKE_ERROR_TEST_DATA)
def test_make_error(param):
    assert errors.make_error(*param["input"]) == param["output"]
