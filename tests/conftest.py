import json
import re
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import pytest
import requests

import credit_engine.constants as CE

SAMPLE_DOI = "10.46936/jejc.proj%2013?48+08-6/60005298"
QUOTED_DOI = quote(SAMPLE_DOI)
SAMPLE_EMAIL = "me@home.com"
QUOTED_EMAIL = quote(SAMPLE_EMAIL)
DEFAULT_EMAIL = "credit_engine@kbase.us"

NOT_FOUND = "NOT_FOUND"
INVALID_DOI = "INVALID_DOI"
A_VALID_DOI = "A_VALID_DOI"
ANOTHER_VALID_DOI = "ANOTHER_VALID_DOI"
A_VALID_DC_DOI = "a_valid_datacite_doi"
A_VALID_XR_DOI = "a_valid_crossref_doi"
INVALID_JSON = "INVALID_JSON"
INVALID_XML = "INVALID_XML"
NO_XML_NODE = "NO_XML_NODE"

SPACE_STR = "      \n\n   \t   "
INVALID_JSON_STR = '{"this": "that"'


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
            "error": re.escape(
                "1 validation error for CleanDoiList\ndoi_list\n  ensure this value has at least 1 items (type=value_error.list.min_items; limit_value=1)",
            ),
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


GET_ENDPOINT_FAIL_DATA = [
    pytest.param(
        {
            "input": [],
            "error": re.escape(
                "1 validation error for GetEndpoint\ndoi\n  field required "
                "(type=value_error.missing)"
            ),
        },
        id="no_args",
    ),
    pytest.param(
        {
            "input": [None],
            "error": re.escape(
                "1 validation error for GetEndpoint\ndoi\n  none is not "
                "an allowed value (type=type_error.none.not_allowed)"
            ),
        },
        id="doi_None",
    ),
    pytest.param(
        {
            "input": [""],
            "error": re.escape(
                "1 validation error for GetEndpoint\ndoi\n  ensure this value "
                "has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="doi_len_0",
    ),
    pytest.param(
        {
            "input": [SPACE_STR],
            "error": re.escape(
                "1 validation error for GetEndpoint\ndoi\n  ensure this value "
                "has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="doi_whitespace",
    ),
    pytest.param(
        {
            "input": ["", ""],
            "error": re.escape(
                "2 validation errors for GetEndpoint\ndoi\n  ensure this value"
                " has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)\n"
                "output_format\n  ensure this value has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="doi_len_0_fmt_len_0",
    ),
    pytest.param(
        {
            "input": [SPACE_STR, SPACE_STR],
            "error": re.escape(
                "2 validation errors for GetEndpoint\ndoi\n  ensure this value"
                " has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)\n"
                "output_format\n  ensure this value has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="doi_whitespace_fmt_whitespace",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, ""],
            "error": re.escape(
                "1 validation error for GetEndpoint\noutput_format\n  ensure "
                "this value has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="fmt_len_0",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, SPACE_STR],
            "error": re.escape(
                "1 validation error for GetEndpoint\noutput_format\n  ensure "
                "this value has at least 1 characters "
                "(type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="fmt_whitespace",
    ),
    pytest.param(
        {
            "input": [SAMPLE_DOI, "TXT"],
            "error": re.escape("Invalid output format: TXT"),
        },
        id="fmt_invalid",
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
        A_VALID_DC_DOI: {
            CE.JSON: "sample_data/datacite/10.25585_1487730.json",
            CE.XML: "sample_data/datacite/10.25585_14877730.xml",
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
        A_VALID_XR_DOI: {
            CE.JSON: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixsd.xml",
        },
    },
    CE.OSTI: {
        A_VALID_DOI: {
            CE.JSON: "sample_data/osti/10.25982_1668075.json",
            CE.XML: "sample_data/osti/10.25982_1668075.xml",
        },
        ANOTHER_VALID_DOI: {
            CE.JSON: "sample_data/osti/10.25982_1722943.json",
            CE.XML: "sample_data/osti/10.25982_1722943.xml",
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


OK_200 = {OK: True, CODE: 200}
NOT_FOUND_404 = {OK: False, CODE: 404}

SOURCE_404 = {
    CE.CROSSREF: {**NOT_FOUND_404, CONTENT: "Resource not found"},
    CE.DATACITE: {
        **NOT_FOUND_404,
        CE.JSON: {
            "errors": [
                {
                    "status": "404",
                    "title": "The resource you are looking for doesn't exist.",
                }
            ]
        },
    },
    CE.OSTI: {
        **NOT_FOUND_404,
        CE.JSON: {
            "errorDescription": "No data found for record SOME_DOI",
            "statusMessage": "Not Found",
            "statusCode": 404,
        },
    },
}


RESPONSE_DATA = {
    # check_doi_source at crossref
    "https://api.crossref.org/works/DATACITE_DOI/agency": {
        **OK_200,
        JSON: {"message": {"agency": {"id": "datacite"}}},
    },
    "https://api.crossref.org/works/CROSSREF_DOI/agency": {
        **OK_200,
        JSON: {"message": {"agency": {"id": "crossref"}}},
    },
    f"https://api.crossref.org/works/{INVALID_JSON}": {
        **OK_200,
        CONTENT: INVALID_JSON_STR,
    },
    # crossref
    f"https://api.crossref.org/works/{A_VALID_XR_DOI}": {
        **OK_200,
        JSON: generate_response_for_doi(CE.CROSSREF, A_VALID_XR_DOI, CE.JSON),
    },
    # datacite
    f"https://api.datacite.org/dois/{A_VALID_DC_DOI}?affiliation=true": {
        **OK_200,
        JSON: generate_response_for_doi(CE.DATACITE, A_VALID_DC_DOI, CE.JSON),
    },
    f"https://api.datacite.org/dois/{INVALID_JSON}?affiliation=true": {
        **OK_200,
        CONTENT: INVALID_JSON_STR,
    },
    f"https://api.datacite.org/dois/{NO_XML_NODE}?affiliation=true": {
        **OK_200,
        JSON: {"this": "that"},
    },
    f"https://api.datacite.org/dois/{INVALID_XML}?affiliation=true": {
        **OK_200,
        JSON: {"data": {"attributes": {"xml": "abcdefghijklmopqrst"}}},
    },
    # osti
    f"https://www.osti.gov/api/v1/records?doi={INVALID_JSON}": {
        **OK_200,
        CONTENT: INVALID_JSON_STR,
    },
    f"https://www.osti.gov/api/v1/records?doi={INVALID_XML}": {
        **OK_200,
        CONTENT: "TODO",
    },
}

# JSON responses
for doi in [A_VALID_DOI, ANOTHER_VALID_DOI]:
    # crossref retrieve_doi
    RESPONSE_DATA[f"https://api.crossref.org/works/{doi}"] = {
        **OK_200,
        JSON: generate_response_for_doi(CE.CROSSREF, doi, CE.JSON),
    }
    # datacite retrieve_doi
    RESPONSE_DATA[f"https://api.datacite.org/dois/{doi}?affiliation=true"] = {
        **OK_200,
        JSON: generate_response_for_doi(CE.DATACITE, doi, CE.JSON),
    }
    # osti
    RESPONSE_DATA[f"https://www.osti.gov/api/v1/records?doi={doi}"] = {
        **OK_200,
        JSON: generate_response_for_doi(CE.OSTI, doi, CE.JSON),
    }

# crossref XML responses
for doi in [A_VALID_DOI, ANOTHER_VALID_DOI, A_VALID_XR_DOI]:
    for fmt in [CE.UNIXREF, CE.UNIXSD]:
        RESPONSE_DATA[
            f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format={fmt}&id={doi}"
        ] = {
            **OK_200,
            CONTENT: generate_response_for_doi(CE.CROSSREF, doi, fmt),
        }


# custom class to be the mock return value of requests.get()
class MockResponse:
    def __init__(self, kwargs: dict[str, Any]):
        if "url" in kwargs:
            # make sure that the OSTI response is in the correct format
            if (
                "headers" in kwargs
                and "Accept" in kwargs["headers"]
                and kwargs["headers"]["Accept"] == "application/xml"
                and kwargs["url"].find("osti") != -1
            ):
                for doi in [A_VALID_DOI, ANOTHER_VALID_DOI]:
                    if kwargs["url"].find(doi) != -1:
                        self.response = {
                            **OK_200,
                            CONTENT: generate_response_for_doi(CE.OSTI, doi, CE.XML),
                        }
                        return

            if kwargs["url"] in RESPONSE_DATA:
                self.response = RESPONSE_DATA[kwargs["url"]]
                return

            # 404s for any other URLs in the crossref/datacite/osti namespaces
            if kwargs["url"].find("crossref") != -1:
                self.response = SOURCE_404[CE.CROSSREF]
            elif kwargs["url"].find("datacite") != -1:
                self.response = SOURCE_404[CE.DATACITE]
            elif kwargs["url"].find("osti") != -1:
                self.response = SOURCE_404[CE.OSTI]
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
    def accept_header(self):
        if "accept_header" in self.response:
            return self.response["accept_header"]
        return None

    @property
    def content(self):
        if CONTENT in self.response:
            return self.response[CONTENT]

        if JSON in self.response:
            return json.dumps(self.response[JSON])

        return ""

    @property
    def ok(self) -> str:
        return self.response[OK]

    @property
    def status_code(self) -> str:
        return self.response[CODE]

    def json(self) -> Union[list, dict]:
        """Mimic the JSON method, which decodes response content to JSON.

        :return: decoded response data
        :rtype: Union[list, dict]
        """
        if JSON in self.response:
            return self.response[JSON]
        return json.loads(self.response[CONTENT])


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
