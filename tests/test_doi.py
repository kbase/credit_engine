import re

import pytest

from credit_engine.errors import make_error
from credit_engine.parsers import crossref, datacite, doi

CHECK_DOI_SOURCE_TEST_DATA = [
    pytest.param(
        {
            "doi": "DATACITE_DOI",
            "expected": "datacite",
        },
        id="datacite",
    ),
    pytest.param(
        {
            "doi": "CROSSREF_DOI",
            "expected": "crossref",
        },
        id="crossref",
    ),
    pytest.param(
        {
            "doi": "NOT_FOUND",
            "expected": None,
        },
        id="not_found",
    ),
]


@pytest.mark.parametrize("param", CHECK_DOI_SOURCE_TEST_DATA)
def test_check_doi_source(param, _mock_response):
    assert doi.check_doi_source(param["doi"]) == param["expected"]


GET_EXTENSION_TEST_DATA = [
    pytest.param(
        {
            "parser": datacite,
            "output_format": "JSON",
            "expected": datacite.FILE_EXTENSIONS["json"],
        },
        id="datacite_json",
    ),
    pytest.param(
        {
            "parser": crossref,
            "output_format": "json",
            "expected": crossref.FILE_EXTENSIONS["json"],
        },
        id="crossref_json",
    ),
    pytest.param(
        {
            "parser": crossref,
            "output_format": "UNIXREF",
            "expected": crossref.FILE_EXTENSIONS["unixref"],
        },
        id="crossref_unixref",
    ),
    pytest.param(
        {
            "parser": crossref,
            "output_format": "xml",
            "error": True,
        },
        id="crossref_xml",
    ),
    pytest.param(
        {
            "parser": datacite,
            "output_format": "unixsd",
            "error": True,
        },
        id="datacite_unixsd",
    ),
]


@pytest.mark.parametrize("param", GET_EXTENSION_TEST_DATA)
def test_get_extension(param):
    if "expected" in param:
        assert (
            doi.get_extension(param["parser"], param["output_format"])
            == param["expected"]
        )
    else:
        error_text = make_error("invalid", {"format": param["output_format"]})
        with pytest.raises(ValueError, match=error_text):
            doi.get_extension(param["parser"], param["output_format"])


RETRIEVE_DOI_LIST_FAIL_TEST_DATA = [
    pytest.param(
        {
            "input": [
                ["VALID_DOI", "ANOTHER_VALID_DOI"],
                None,
                None,
                "THE BOWELS OF HELL",
            ],
            "error": "Invalid data source: THE BOWELS OF HELL",
        },
        id="invalid_source",
    ),
    pytest.param(
        {
            "input": [
                ["VALID_DOI", "ANOTHER_VALID_DOI"],
                None,
                None,
                "datacite",
                ["rdfxml", "json", "duck types"],
            ],
            "error": re.escape(
                make_error("invalid", {"format": ["rdfxml", "duck types"]})
            ),
        },
        id="invalid_format",
    ),
]


@pytest.mark.parametrize("param", RETRIEVE_DOI_LIST_FAIL_TEST_DATA)
def test_retrieve_doi_list_fail(param):
    with pytest.raises(ValueError, match=param["error"]):
        doi.retrieve_doi_list(*param["input"])
