import json
import re
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import pytest
import requests

import credit_engine.constants as CE
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
CONTENT = "content"
JSON = CE.JSON

# input for cleaning up DOI lists
CLEAN_DOI_LIST_DATA = [
    pytest.param(
        {
            "input": None,
            "error": re.escape(
                "1 validation error for CleanDoiList\ndoi_list\n  none is not an allowed value (type=type_error.none.not_allowed)"
            ),
        },
        id="None_input",
    ),
    pytest.param(
        {
            "input": A_VALID_DOI,
            "error": re.escape(
                "1 validation error for CleanDoiList\ndoi_list\n  value is not a valid list (type=type_error.list)"
            ),
        },
        id="invalid_input_type",
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
            "input": [""],
            "error": re.escape(
                "1 validation error for CleanDoiList\ndoi_list -> 0\n  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="zero_str_length",
    ),
    pytest.param(
        {
            "input": [None, "       ", "    ", "  \t  \n\n", ""],
            "error": re.escape(
                "5 validation errors for CleanDoiList\ndoi_list -> 0\n  none is not an allowed value (type=type_error.none.not_allowed)"
            ),
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
    pytest.param(
        {
            "input": [A_VALID_DOI, ANOTHER_VALID_DOI, INVALID_DOI, NOT_FOUND],
            "output": [A_VALID_DOI, ANOTHER_VALID_DOI, INVALID_DOI, NOT_FOUND],
        },
        id="all_ok",
    ),
]


DATA_FILES = {
    CE.DATACITE: {
        A_VALID_DOI: {
            CE.JSON: "sample_data/datacite/10.25585_1487552.json",
            CE.XML: "sample_data/datacite/10.25585_1487552.xml",
        },
        ANOTHER_VALID_DOI: {
            CE.JSON: "sample_data/datacite/10.25585_1487554.json",
            CE.XML: "sample_data/datacite/10.25585_1487554.xml",
        },
    },
    CE.CROSSREF: {
        A_VALID_DOI: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60007526.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_10.25585_60007526.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_10.25585_60007526.unixsd.xml",
        },
        ANOTHER_VALID_DOI: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60007530.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_10.25585_60007530.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_10.25585_60007530.unixsd.xml",
        },
    },
}


def generate_response(file_path: str) -> Union[None, bytes, str, list, dict]:
    current_dir = Path.cwd()
    path_to_file = Path.resolve(current_dir.joinpath(Path(file_path)))
    if path_to_file.suffix == f".{CE.JSON}":
        with open(path_to_file, encoding="utf-8") as fh:
            file_data = json.load(fh)
            return file_data

    return path_to_file.read_bytes()


def generate_response_for_doi(
    source: str, doi: str, fmt: str
) -> Union[None, bytes, str, list, dict]:
    """Generate a response for a given DOI

    :param source: data source
    :type source: str
    :param doi: DOI
    :type doi: str
    :param fmt: format
    :type fmt: str
    :return: the appropriate response - may be a JSON data structure or XML
    :rtype: Union[None, bytes, str, list, dict]
    """
    if (
        source in DATA_FILES
        and doi in DATA_FILES[source]
        and fmt in DATA_FILES[source][doi]
    ):
        return generate_response(DATA_FILES[source][doi][fmt])
    return None


def generate_doi_data(data_files):
    DOI_DATA = {}
    for source in data_files.keys():
        for doi in data_files[source].keys():
            for fmt in data_files[source][doi].keys():
                DOI_DATA[f"{source}_{doi}_{fmt}"] = generate_response(
                    data_files[source][doi][fmt]
                )
    DOI_DATA[A_VALID_DOI] = DOI_DATA[f"{CE.DATACITE}_{A_VALID_DOI}_{CE.JSON}"]
    DOI_DATA[ANOTHER_VALID_DOI] = DOI_DATA[
        f"{CE.DATACITE}_{ANOTHER_VALID_DOI}_{CE.JSON}"
    ]

    return DOI_DATA


OK_200 = {OK: True, CODE: 200}
NOT_FOUND_404 = {OK: False, CODE: 404}

CROSSREF_404 = {**NOT_FOUND_404, CONTENT: "Resource not found"}
DATACITE_404 = {
    **NOT_FOUND_404,
    CE.JSON: {
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
    f"https://api.crossref.org/works/{A_VALID_DOI}": generate_response_for_doi(
        CE.CROSSREF, A_VALID_DOI, CE.JSON
    ),
    f"https://api.crossref.org/works/{ANOTHER_VALID_DOI}": generate_response_for_doi(
        CE.CROSSREF, ANOTHER_VALID_DOI, CE.JSON
    ),
    # datacite retrieve_doi
    f"https://api.datacite.org/dois/{A_VALID_DOI}?affiliation=true": generate_response_for_doi(
        CE.DATACITE, A_VALID_DOI, CE.JSON
    ),
    f"https://api.datacite.org/dois/{ANOTHER_VALID_DOI}?affiliation=true": generate_response_for_doi(
        CE.DATACITE, ANOTHER_VALID_DOI, CE.JSON
    ),
}


RESPONSE_DATA = {
    f"https://api.crossref.org/works/{NOT_FOUND}/agency": CROSSREF_404,
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={A_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.UNIXSD),
    },
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixref&id={A_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response_for_doi(CE.CROSSREF, A_VALID_DOI, CE.UNIXREF),
    },
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={ANOTHER_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response_for_doi(CE.CROSSREF, ANOTHER_VALID_DOI, CE.UNIXSD),
    },
    f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixref&id={ANOTHER_VALID_DOI}": {
        **OK_200,
        CONTENT: generate_response_for_doi(CE.CROSSREF, ANOTHER_VALID_DOI, CE.UNIXREF),
    },
    f"https://api.crossref.org/works/{INVALID_DOI}": CROSSREF_404,
    f"https://api.crossref.org/works/{NOT_FOUND}": CROSSREF_404,
    f"https://api.datacite.org/dois/{NOT_FOUND}?affiliation=true": DATACITE_404,
    f"https://api.datacite.org/dois/{INVALID_DOI}?affiliation=true": DATACITE_404,
}


# custom class to be the mock return value of requests.get()
class MockResponse:
    def __init__(self, kwargs: dict[str, Any]):
        if "url" in kwargs:
            if kwargs["url"] in RESPONSE_JSON:
                self.response = {**OK_200, JSON: RESPONSE_JSON[kwargs["url"]]}
                return
            if kwargs["url"] in RESPONSE_DATA:
                self.response = RESPONSE_DATA[kwargs["url"]]
                return

            if kwargs["url"].find("crossref") != -1:
                self.response = CROSSREF_404
            elif kwargs["url"].find("datacite") != -1:
                self.response = DATACITE_404

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
