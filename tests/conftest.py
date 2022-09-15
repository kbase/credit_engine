import json
from typing import Any, Union
from urllib.parse import quote

import pytest
import requests

SAMPLE_DOI = "10.46936/jejc.proj%2013?48+08-6/60005298"
QUOTED_DOI = quote(SAMPLE_DOI)
SAMPLE_EMAIL = "me@home.com"
QUOTED_EMAIL = quote(SAMPLE_EMAIL)

NOT_FOUND = "NOT_FOUND"
INVALID_DOI = "INVALID_DOI"
VALID_DOI = "VALID_DOI"
ANOTHER_VALID_DOI = "ANOTHER_VALID_DOI"


OK = "ok"
CODE = "status_code"
JSON = "json"
CONTENT = "content"

DOI_DATA = {
    "VALID_DOI": {"this": "is", "not": "a", "dict": {}},
    "ANOTHER_VALID_DOI": {"this": ["is", "different", "apparently"]},
}


CLEAN_DOI_LIST_DATA = [
    pytest.param(
        {
            "input": [VALID_DOI, ANOTHER_VALID_DOI, INVALID_DOI, NOT_FOUND],
            "output": [VALID_DOI, ANOTHER_VALID_DOI, INVALID_DOI, NOT_FOUND],
        },
        id="all_ok",
    ),
    pytest.param(
        {
            "input": VALID_DOI,
            "error": "DOI list must be a list of strings with non-zero length",
        },
        id="wrong_input",
    ),
    pytest.param(
        {
            "input": [],
            "error": "DOI list must be a list of strings with non-zero length",
        },
        id="zero_length_list_input",
    ),
    pytest.param(
        {
            "input": None,
            "error": "DOI list must be a list of strings with non-zero length",
        },
        id="None_input",
    ),
    pytest.param(
        {
            "input": [None, "       ", "    ", "  \t  \n\n", ""],
            "error": "No valid DOIs found in doi list",
        },
        id="spaced_out",
    ),
    pytest.param(
        {
            "input": [10.12345, 12345, r"     ANOTHER_VALID_DOI       "],
            "output": ["10.12345", "12345", ANOTHER_VALID_DOI],
        },
        id="format_conversion",
    ),
    pytest.param(
        {
            "input": [
                f"  {VALID_DOI} ",
                INVALID_DOI,
                VALID_DOI,
                INVALID_DOI,
                f"   {VALID_DOI}\n\n",
            ],
            "output": [VALID_DOI, INVALID_DOI],
        },
        id="duplicates",
    ),
]


RESPONSE_DATA = {
    # check_doi_source
    "https://api.crossref.org/works/DATACITE_DOI/agency": {
        OK: True,
        CODE: 200,
        JSON: {"message": {"agency": {"id": "datacite"}}},
    },
    "https://api.crossref.org/works/CROSSREF_DOI/agency": {
        OK: True,
        CODE: 200,
        JSON: {"message": {"agency": {"id": "crossref"}}},
    },
    # returns a 404
    "https://api.crossref.org/works/NOT_FOUND/agency": {
        OK: False,
        CODE: 404,
        CONTENT: "Resource not found.",
    },
    # datacite retrieve_doi
    "https://api.datacite.org/dois/NOT_FOUND?affiliation=true": {
        OK: False,
        CODE: 404,
        JSON: {
            "errors": [
                {
                    "status": "404",
                    "title": "The resource you are looking for doesn't exist.",
                }
            ]
        },
    },
    "https://api.datacite.org/dois/INVALID_DOI?affiliation=true": {
        OK: False,
        CODE: 404,
        JSON: {
            "errors": [
                {
                    "status": "404",
                    "title": "The resource you are looking for doesn't exist.",
                }
            ]
        },
    },
    "https://api.datacite.org/dois/VALID_DOI?affiliation=true": {
        OK: True,
        CODE: 200,
        JSON: {"this": "is", "not": "a", "dict": {}},
    },
    "https://api.datacite.org/dois/ANOTHER_VALID_DOI?affiliation=true": {
        OK: True,
        CODE: 200,
        JSON: {"this": ["is", "different", "apparently"]},
    },
}


VALID_DOI_LIST = {
    "id": "all_valid",
    "input": ["VALID_DOI", "ANOTHER_VALID_DOI"],
    "output": {
        "data": {
            "VALID_DOI": DOI_DATA["VALID_DOI"],
            "ANOTHER_VALID_DOI": DOI_DATA["ANOTHER_VALID_DOI"],
        }
    },
    "file_list": [],
}
SEMI_VALID_DOI_LIST = {
    "id": "semi_valid",
    "input": ["VALID_DOI", "NOT_FOUND"],
    "output": {
        "data": {
            "VALID_DOI": DOI_DATA["VALID_DOI"],
        }
    },
    "file_list": [],
    "errors": ["Request for NOT_FOUND failed with status code 404"],
}
INVALID_DOI_LIST = {
    "id": "all_invalid",
    "input": ["NOT_FOUND", "INVALID_DOI"],
    "output": {"data": {}},
    "file_list": [],
    "errors": [
        "Request for NOT_FOUND failed with status code 404",
        "Request for INVALID_DOI failed with status code 404",
    ],
}

RETRIEVE_DOI_LIST_TEST_DATA = []

# add in save_files and save_dir
for p in [VALID_DOI_LIST, SEMI_VALID_DOI_LIST, INVALID_DOI_LIST]:
    # no save_files param
    RETRIEVE_DOI_LIST_TEST_DATA.append(pytest.param(p, id=p["id"]))

    # save_files OFF
    RETRIEVE_DOI_LIST_TEST_DATA.append(
        pytest.param(
            {
                **p,
                "save_files": False,
                "save_dir": "tmp_path",
            },
            id=p["id"] + "_no_save",
        )
    )

    # save to a temp dir
    RETRIEVE_DOI_LIST_TEST_DATA.append(
        pytest.param(
            {
                **p,
                "save_files": True,
                "save_dir": "tmp_path",
                "file_list": [doi + ".json" for doi in p["output"]["data"].keys()],
            },
            id=p["id"] + "_save_to_dir",
        )
    )

    # save to default dir
    RETRIEVE_DOI_LIST_TEST_DATA.append(
        pytest.param(
            {
                **p,
                "save_files": True,
                "file_list": [doi + ".json" for doi in p["output"]["data"].keys()],
            },
            id=p["id"] + "_save_to_default_dir",
        )
    )


# custom class to be the mock return value of requests.get()
class MockResponse:
    def __init__(self, *args: str, **kwargs: dict[str, Union[str, list, dict]]):
        self.request_url = args[0]
        self.response = RESPONSE_DATA[self.request_url]

    @property
    def content(self):
        if self.response[CONTENT]:
            return self.response[CONTENT].encode()

        if self.response[JSON]:
            return json.dumps(self.response[JSON]).encode()

        return ""

    @property
    def ok(self) -> str:
        return self.response[OK]

    @property
    def status_code(self) -> str:
        return self.response[CODE]

    def json(self) -> Union[list, dict]:
        return self.response[JSON]


# monkeypatched requests.get moved to a fixture
@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def mock_get(*args: list[str], **kwargs: dict[str, Any]):
        return MockResponse(*args, **kwargs)

    monkeypatch.setattr(requests, "get", mock_get)
