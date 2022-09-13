import json

import pytest
import requests

from credit_engine.parsers.doi import check_doi_source

response_data = {
    "https://api.crossref.org/works/DATACITE_DOI/agency": {
        "ok": True,
        "status_code": 200,
        "json": {"message": {"agency": {"id": "datacite"}}},
    },
    "https://api.crossref.org/works/CROSSREF_DOI/agency": {
        "ok": True,
        "status_code": 200,
        "json": {"message": {"agency": {"id": "crossref"}}},
    },
    # returns a 404
    "https://api.crossref.org/works/NOT_FOUND/agency": {
        "ok": False,
        "status_code": 404,
        "content": "Resource not found.",
    },
}


# custom class to be the mock return value of requests.get()
class MockResponse:
    def __init__(self, *args, **kwargs):
        self.request = args[0]
        self.response = response_data[self.request]

    @property
    def content(self):
        if self.response["content"]:
            return self.response["content"].encode()

        if self.response["json"]:
            return json.dumps(self.response["json"]).encode()

    @property
    def ok(self):
        return self.response["ok"]

    @property
    def status_code(self):
        return self.response["status_code"]

    def json(self):
        return self.response["json"]


# monkeypatched requests.get moved to a fixture
@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def mock_get(*args, **kwargs):
        return MockResponse(*args, **kwargs)

    monkeypatch.setattr(requests, "get", mock_get)


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
def test_check_doi_source(param, mock_response):
    assert check_doi_source(param["doi"]) == param["expected"]
