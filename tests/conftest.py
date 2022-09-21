import json
from importlib.resources import path
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import pytest
import requests

from credit_engine.errors import ERROR_STRING

SAMPLE_DOI = "10.46936/jejc.proj%2013?48+08-6/60005298"
QUOTED_DOI = quote(SAMPLE_DOI)
SAMPLE_EMAIL = "me@home.com"
QUOTED_EMAIL = quote(SAMPLE_EMAIL)
DEFAULT_EMAIL = "credit_engine@kbase.us"

NOT_FOUND = "NOT_FOUND"
INVALID_DOI = "INVALID_DOI"
A_VALID_DOI = "A_VALID_DOI"
ANOTHER_VALID_DOI = "ANOTHER_VALID_DOI"

OK = "ok"
CODE = "status_code"
JSON = "json"
CONTENT = "content"
XML = "xml"
UNIXREF = "unixref"
UNIXSD = "unixsd"


# input for cleaning up DOI lists
CLEAN_DOI_LIST_DATA = [
    pytest.param(
        {
            "input": [A_VALID_DOI, ANOTHER_VALID_DOI, INVALID_DOI, NOT_FOUND],
            "output": [A_VALID_DOI, ANOTHER_VALID_DOI, INVALID_DOI, NOT_FOUND],
        },
        id="all_ok",
    ),
    pytest.param(
        {
            "input": A_VALID_DOI,
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
            "input": [10.12345, 12345, f"     {ANOTHER_VALID_DOI}       "],
            "output": ["10.12345", "12345", ANOTHER_VALID_DOI],
        },
        id="format_conversion",
    ),
    pytest.param(
        {
            "input": [
                f"  {A_VALID_DOI} ",
                INVALID_DOI,
                A_VALID_DOI,
                INVALID_DOI,
                f"   {A_VALID_DOI}\n\n",
            ],
            "output": [A_VALID_DOI, INVALID_DOI],
        },
        id="duplicates",
    ),
]


def generate_response(file_path: str):
    current_dir = Path.cwd()
    path_to_file = Path.resolve(current_dir.joinpath(Path(file_path)))
    if path_to_file.suffix == f".{JSON}":
        print('importing as JSON')
        with open(path_to_file, encoding="utf-8") as fh:
            file_data = json.load(fh)
            return file_data

    print('reading as bytes')
    return path_to_file.read_bytes()


DATA_FILES = {
    'DATACITE': {
        A_VALID_DOI: {
            JSON: "sample_data/datacite/10.25585_1487552.json",
            XML: "sample_data/datacite/10.25585_1487552.xml",
        },
        ANOTHER_VALID_DOI: {
            JSON: "sample_data/datacite/10.25585_1487554.json",
            XML: "sample_data/datacite/10.25585_1487554.xml",
        },
    },
    'CROSSREF': {
        A_VALID_DOI: {
            JSON: "sample_data/crossref/10.46936_10.25585_60007526.json",
            UNIXREF: "sample_data/crossref/10.46936_10.25585_60007526.unixref.xml",
            UNIXSD: "sample_data/crossref/10.46936_10.25585_60007526.unixsd.xml",
        },
        ANOTHER_VALID_DOI: {
            JSON: "sample_data/crossref/10.46936_10.25585_60007530.json",
            UNIXREF: "sample_data/crossref/10.46936_10.25585_60007530.unixref.xml",
            UNIXSD: "sample_data/crossref/10.46936_10.25585_60007530.unixsd.xml",
        },
    }
}

DOI_DATA = {doi: generate_response(DATA_FILES[source][doi][JSON]) for doi in [A_VALID_DOI, ANOTHER_VALID_DOI]
for source in ['DATACITE', 'CROSSREF']}


OK_200 = {OK: True, CODE: 200}
NOT_FOUND_404 = {OK: False, CODE: 404}

DATA = {
    A_VALID_DOI: {
        **OK_200,
        JSON: DOI_DATA[A_VALID_DOI],
    },
    ANOTHER_VALID_DOI: {
        **OK_200,
        JSON: DOI_DATA[ANOTHER_VALID_DOI],
    },
}

CROSSREF_404 = {**NOT_FOUND_404, CONTENT: "Resource not found"}
DATACITE_404 = {
    **NOT_FOUND_404,
    JSON: {
        "errors": [
            {
                "status": "404",
                "title": "The resource you are looking for doesn't exist.",
            }
        ]
    },
}

RESPONSE_JSON = {
    # check_doi_source at crossref
    "https://api.crossref.org/works/DATACITE_DOI/agency": {
        "message": {"agency": {"id": "datacite"}},
    },
    "https://api.crossref.org/works/CROSSREF_DOI/agency": {
        "message": {"agency": {"id": "crossref"}},
    },
    # crossref retrieve_doi
    f"https://api.crossref.org/works/{A_VALID_DOI}": generate_response(DATA_FILES['CROSSREF'][A_VALID_DOI][JSON]),
    f"https://api.crossref.org/works/{ANOTHER_VALID_DOI}": generate_response(DATA_FILES['CROSSREF'][ANOTHER_VALID_DOI][JSON]),
    # datacite retrieve_doi
    f"https://api.datacite.org/dois/{A_VALID_DOI}?affiliation=true": generate_response(DATA_FILES['DATACITE'][A_VALID_DOI][JSON]),
    f"https://api.datacite.org/dois/{ANOTHER_VALID_DOI}?affiliation=true": generate_response(DATA_FILES['DATACITE'][ANOTHER_VALID_DOI][JSON]),
}


RESPONSE_DATA = {
    # "https://api.crossref.org/works/DATACITE_DOI/agency": {
    #     **OK_200,
    #     JSON: {"message": {"agency": {"id": "datacite"}}},
    # },
    # "https://api.crossref.org/works/CROSSREF_DOI/agency": {
    #     **OK_200,
    #     JSON: {"message": {"agency": {"id": "crossref"}}},
    # },

    # check_doi_source
    # returns a 404
    f"https://api.crossref.org/works/{NOT_FOUND}/agency": CROSSREF_404,

    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={A_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response(DATA_FILES['CROSSREF'][A_VALID_DOI][UNIXSD]),
    },
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixref&id={A_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response(DATA_FILES['CROSSREF'][A_VALID_DOI][UNIXREF]),
    },
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={ANOTHER_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response(DATA_FILES['CROSSREF'][ANOTHER_VALID_DOI][UNIXSD]),
    },
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixref&id={ANOTHER_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response(DATA_FILES['CROSSREF'][ANOTHER_VALID_DOI][UNIXREF]),
    },
    f"https://api.crossref.org/works/{INVALID_DOI}": CROSSREF_404,
    f"https://api.crossref.org/works/{NOT_FOUND}": CROSSREF_404,
    # 'https://doi.crossref.org/servlet/query?pid={email_address}&format={lc_output_format}&id={quote(doi)}'
    f"https://api.datacite.org/dois/{NOT_FOUND}?affiliation=true": DATACITE_404,
    f"https://api.datacite.org/dois/{INVALID_DOI}?affiliation=true": DATACITE_404,
}


A_VALID_DOI_LIST = {
    "id": "all_valid",
    "input": [A_VALID_DOI, ANOTHER_VALID_DOI],
    "output": {
        "data": {
            A_VALID_DOI: {JSON: DOI_DATA[A_VALID_DOI]},
            ANOTHER_VALID_DOI: {JSON: DOI_DATA[ANOTHER_VALID_DOI]},
        }
    },
    "file_list": [],
}
SEMI_VALID_DOI_LIST = {
    "id": "semi_valid",
    "input": [A_VALID_DOI, NOT_FOUND],
    "output": {
        "data": {
            A_VALID_DOI: {
                JSON: DOI_DATA[A_VALID_DOI],
            },
            NOT_FOUND: {
                JSON: None,
            },
        }
    },
    "file_list": [],
    "errors": ["Request for NOT_FOUND json failed with status code 404"],
}
INVALID_DOI_LIST = {
    "id": "all_invalid",
    "input": [NOT_FOUND, INVALID_DOI],
    "output": {
        "data": {
            NOT_FOUND: {JSON: None},
            INVALID_DOI: {JSON: None},
        }
    },
    "file_list": [],
    "errors": [
        "Request for NOT_FOUND json failed with status code 404",
        "Request for INVALID_DOI json failed with status code 404",
    ],
}

RETRIEVE_DOI_LIST_TEST_DATA = []
SUFFIX = JSON

# add in save_files and save_dir
for p in [A_VALID_DOI_LIST, SEMI_VALID_DOI_LIST, INVALID_DOI_LIST]:
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
                "file_list": [
                    f"{doi}.{SUFFIX}"
                    for doi in p["output"]["data"]
                    if p["output"]["data"][doi][JSON]
                ],
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
                "file_list": [
                    f"{doi}.{SUFFIX}"
                    for doi in p["output"]["data"]
                    if p["output"]["data"][doi][JSON]
                ],
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
                    if doi in [A_VALID_DOI, ANOTHER_VALID_DOI]
                ],
            },
            id=p["id"] + "_save_to_invalid_dir",
        )
    )


# custom class to be the mock return value of requests.get()
class MockResponse:
    def __init__(self, kwargs: dict[str, Any]):
        if "url" in kwargs:
            if kwargs["url"] in RESPONSE_JSON:
                self.response = {
                    **OK_200,
                    JSON: RESPONSE_JSON[kwargs["url"]]
                }
                return
            if kwargs["url"] in RESPONSE_DATA:
                self.response = RESPONSE_DATA[kwargs["url"]]
                return

            if kwargs["url"].find("crossref") != -1:
                self.response = CROSSREF_404
            elif kwargs["url"].find("datacite") != -1:
                self.response = DATACITE_404

            # elif kwargs["url"].find(INVALID_DOI) > -1 or kwargs["url"].find(NOT_FOUND) > -1:
            else:
                raise ValueError(f'No suitable response for url {kwargs["url"]}')

            return

        if JSON in kwargs:
            self.response = {JSON: kwargs[JSON]}
        elif CONTENT in kwargs:
            self.response = {CONTENT: kwargs[CONTENT]}
        else:
            self.response = kwargs

    @property
    def content(self):
        if self.response[CONTENT]:
            return self.response[CONTENT]

        if self.response[JSON]:
            return json.dumps(self.response[JSON])

        return ""

    @property
    def ok(self) -> str:
        return self.response[OK]

    @property
    def status_code(self) -> str:
        return self.response[CODE]

    def json(self) -> Union[list, dict]:
        """Mimic the JSON method, which decodes response content to produce JSON data.

        :return: decoded response data
        :rtype: Union[list, dict]
        """
        return self.response[JSON]


# monkeypatched requests.get moved to a fixture
@pytest.fixture(name="_mock_response")
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
