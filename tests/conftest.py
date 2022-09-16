import json
from typing import Any, Optional, Union
from urllib.parse import quote

import pytest
import requests

from credit_engine.errors import ERROR_STRING

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
            "error": ERROR_STRING["doi_list_format"],
        },
        id="wrong_input",
    ),
    pytest.param(
        {
            "input": [],
            "error": ERROR_STRING["doi_list_format"],
        },
        id="zero_length_list_input",
    ),
    pytest.param(
        {
            "input": None,
            "error": ERROR_STRING["doi_list_format"],
        },
        id="None_input",
    ),
    pytest.param(
        {
            "input": [None, "       ", "    ", "  \t  \n\n", ""],
            "error": ERROR_STRING["no_valid_dois"],
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

DATA = {
    NOT_FOUND: {OK: False, CODE: 404, CONTENT: "Resource not found"},
    VALID_DOI: {
        OK: True,
        CODE: 200,
        JSON: {"this": "is", "not": "a", "dict": {}},
    },
    ANOTHER_VALID_DOI: {
        OK: True,
        CODE: 200,
        JSON: {"this": ["is", "different", "apparently"]},
    },
}

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
    "https://api.crossref.org/works/NOT_FOUND/agency": DATA[NOT_FOUND],
    # crossref retrieve_doi
    "https://api.crossref.org/works/VALID_DOI": DATA[VALID_DOI],
    "https://api.crossref.org/works/ANOTHER_VALID_DOI": DATA[ANOTHER_VALID_DOI],
    "https://api.crossref.org/works/INVALID_DOI": DATA[NOT_FOUND],
    "https://api.crossref.org/works/NOT_FOUND": DATA[NOT_FOUND],
    # 'https://doi.crossref.org/servlet/query?pid={email_address}&format={lc_output_format}&id={quote(doi)}'
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
    "https://api.datacite.org/dois/VALID_DOI?affiliation=true": DATA[VALID_DOI],
    "https://api.datacite.org/dois/ANOTHER_VALID_DOI?affiliation=true": DATA[
        ANOTHER_VALID_DOI
    ],
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
SUFFIX = "json"

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
                "file_list": [f"{doi}.{SUFFIX}" for doi in p["output"]["data"]],
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
                "file_list": [f"{doi}.{SUFFIX}" for doi in p["output"]["data"]],
            },
            id=p["id"] + "_save_to_default_dir",
        )
    )

    # save to an invalid dir
    RETRIEVE_DOI_LIST_TEST_DATA.append(
        pytest.param(
            {
                **p,
                "save_files": True,
                "save_dir": "/does/not/exist",
                "file_list": [],
                # only valid DOIs will have the file not found error
                "errors": p.get("errors", [])
                + [
                    f"[Errno 2] No such file or directory: '/does/not/exist/{doi}.{SUFFIX}'"
                    for doi in p["input"]
                    if doi in [VALID_DOI, ANOTHER_VALID_DOI]
                ],
            },
            id=p["id"] + "_save_to_invalid_dir",
        )
    )


# custom class to be the mock return value of requests.get()
class MockResponse:
    def __init__(self, kwargs: dict[str, Any]):
        print("args to __init__")
        print(kwargs)
        if "url" in kwargs:
            self.response = RESPONSE_DATA[kwargs["url"]]
            return

        if "json" in kwargs:
            self.response = {JSON: kwargs["json"]}
        elif "content" in kwargs:
            self.response = {CONTENT: kwargs["content"]}
        else:
            self.response = kwargs

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
@pytest.fixture(name="mock_response")
def mock_response(monkeypatch):
    """Requests.get() returns a MockResponse object"""

    def mock_get(url: str, params: Optional[dict] = None, **kwargs: Optional[dict]):
        if params is None:
            params = {}
        response_args = {**params, **kwargs}

        if url:
            response_args["url"] = url
        return MockResponse(response_args)

    monkeypatch.setattr(requests, "get", mock_get)
