import pytest

import credit_engine.errors as errors
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
            "input": ["invalid", {}],
            "output": ERROR_STRING["invalid"],
        },
        id="invalid_empty_args",
    ),
    pytest.param(
        {
            "input": ["invalid", {"this": "that"}],
            "output": "Invalid output format: FORMAT",
        },
        id="invalid_invalid_args",
    ),
    pytest.param(
        {
            "input": ["invalid", {"format": "koala"}],
            "output": "Invalid output format: koala",
        },
        id="invalid_valid_args",
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
