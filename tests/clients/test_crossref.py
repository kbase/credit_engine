import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients.crossref import (
    ClientArgs,
    check_doi_source,
    get_endpoint,
    retrieve_doi,
)
from tests.common import check_stdout_for_errs
from tests.conftest import (
    INVALID_JSON,
    NOT_FOUND_DOI_A,
    QUOTED_DEFAULT_EMAIL,
    QUOTED_DOI,
    QUOTED_EMAIL,
    SAMPLE_DOI,
    SAMPLE_EMAIL,
    VALID_DC_DOI,
    VALID_XR_DOI,
    VALID_XR_DOI_A,
    VALID_XR_DOI_B,
    generate_response_for_doi,
)

GET_ENDPOINT_TEST_DATA = [
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": CE.OutputFormat.JSON},
            "args": {},
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_json",
    ),
    pytest.param(
        {
            "input": {
                "doi": SAMPLE_DOI,
                "output_format": CE.OutputFormat.JSON,
            },
            "args": {
                "email_address": SAMPLE_EMAIL,
            },
            "expected": f"https://api.crossref.org/works/{QUOTED_DOI}",
        },
        id="fmt_json_with_email",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": CE.OutputFormat.XML},
            "args": {},
            "expected": f"https://doi.crossref.org/servlet/query?format=unixsd&id={QUOTED_DOI}&pid={QUOTED_DEFAULT_EMAIL}",
        },
        id="fmt_xml",
    ),
    pytest.param(
        {
            "input": {
                "doi": SAMPLE_DOI,
                "output_format": CE.OutputFormat.XML,
            },
            "args": {
                "email_address": SAMPLE_EMAIL,
            },
            "expected": f"https://doi.crossref.org/servlet/query?format=unixsd&id={QUOTED_DOI}&pid={QUOTED_EMAIL}",
        },
        id="fmt_xml_with_email",
    ),
]


@pytest.mark.parametrize("param", GET_ENDPOINT_TEST_DATA)
def test_get_endpoint(param):
    client_args = ClientArgs(source=CE.CROSSREF, **param["args"])

    if "expected" in param:
        assert get_endpoint(client_args, **param["input"]) == param["expected"]
    else:
        with pytest.raises(ValueError, match=param["error"]):
            get_endpoint(**param["input"])  # type: ignore


fmt_list = {CE.JSON, CE.XML}
RETRIEVE_DOI_TEST_DATA = [
    pytest.param(
        {
            "input": {"doi": VALID_XR_DOI_A},
            "expected": {
                CE.JSON: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_A, CE.JSON)
            },
        },
        id="ok_default_format",
    ),
    pytest.param(
        {
            "input": {"doi": VALID_XR_DOI_A, "output_formats": {CE.OutputFormat.JSON}},
            "expected": {
                CE.JSON: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_A, CE.JSON)
            },
        },
        id="ok_fmt_json",
    ),
    pytest.param(
        {
            "input": {"doi": VALID_XR_DOI_A, "output_formats": {CE.OutputFormat.XML}},
            "expected": {
                CE.XML: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_A, CE.XML)
            },
        },
        id="ok_fmt_xml",
    ),
    pytest.param(
        {
            "input": {"doi": VALID_XR_DOI_B, "output_formats": fmt_list},
            "expected": {
                fmt: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_B, fmt)
                for fmt in fmt_list
            },
        },
        id="ok_fmt_list",
    ),
    pytest.param(
        {
            "input": {"doi": NOT_FOUND_DOI_A},
            "expected": {CE.JSON: None},
            "stdout": [
                f"Request for {NOT_FOUND_DOI_A} {CE.JSON} failed with status code 404"
            ],
        },
        id="fail_default_format",
    ),
    pytest.param(
        {
            "input": {"doi": NOT_FOUND_DOI_A, "output_formats": fmt_list},
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
            "input": {"doi": INVALID_JSON, "output_formats": {CE.OutputFormat.JSON}},
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
    client_args = ClientArgs(source=CE.CROSSREF, **param["input"])

    if "error" in param:
        with pytest.raises(ValueError, match=param["error"]):
            retrieve_doi(client_args, param["input"]["doi"])
        return

    assert retrieve_doi(client_args, param["input"]["doi"]) == param["expected"]
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


@pytest.mark.usefixtures("_mock_response")
@pytest.mark.parametrize("param", CHECK_DOI_SOURCE_TEST_DATA)
def test_check_doi_source(param):
    """Test the DOI source function.

    :param param: doi: the DOI to query; expected: expected result
    :type param: pytest.param
    :param _mock_response: mock requests.get function
    :type _mock_response: pytest mock
    """
    assert check_doi_source(param["doi"]) == param["expected"]
