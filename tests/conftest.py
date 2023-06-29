import json
import re
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import pytest
import requests

import credit_engine.constants as CE
from credit_engine.util import full_path

SAMPLE_DOI = "10.46936/jejc.proj%2013?48+08-6/60005298"
QUOTED_DOI = quote(SAMPLE_DOI)
SAMPLE_EMAIL = "me@home.com"
QUOTED_EMAIL = quote(SAMPLE_EMAIL)
QUOTED_DEFAULT_EMAIL = quote(CE.DEFAULT_EMAIL)

INVALID_JSON = "INVALID_JSON"
INVALID_XML = "INVALID_XML"
NO_XML_NODE = "NO_XML_NODE"

# hashtag, question mark, percent sign -- valid / common URI characters
VALID_DOI_A = r"10.1000/12%34?56.78#90"
# all possible special characters
# N.b. syntax highlighting may be wrong
VALID_DOI_B = r'10.100/%"# ?.<>{}^[]`|\+'
VALID_DC_DOI = r"10.12345/d@*c1t3.(uri)"
VALID_XR_DOI = r"10.12345/†r05{2}?ef*(uri)"

VALID_DC_DOI_A = r"10.25982/90997.49/1783189"
VALID_DC_DOI_B = r"10.25982/54100.27/1635639"
VALID_XR_DOI_A = r"10.46936/jejc.proj.2013.48086/60005298"
VALID_XR_DOI_B = r"10.46936/10.25585/60001190"
NOT_FOUND_DOI_A = "10.25585/0000000000"
NOT_FOUND_DOI_B = "00.00000/0000000000"

FILE_NAME = {
    VALID_DC_DOI_A: "10.25982_90997.49_1783189",
    VALID_DC_DOI_B: "10.25982_54100.27_1635639",
    VALID_XR_DOI_A: "10.46936_jejc.proj.2013.48086_60005298",
    VALID_XR_DOI_B: "10.46936_10.25585_60001190",
    NOT_FOUND_DOI_A: "10.25585_0000000000",
    NOT_FOUND_DOI_B: "00.00000_0000000000",
    VALID_DC_DOI: "10.12345_d_c1t3._uri_",
    VALID_XR_DOI: "10.12345_r05_2_ef_uri_",
    VALID_DOI_A: "10.1000_12_34_56.78_90",
    VALID_DOI_B: "10.100_._",
}

URI = {
    NOT_FOUND_DOI_A: quote(NOT_FOUND_DOI_A),
    NOT_FOUND_DOI_B: quote(NOT_FOUND_DOI_B),
    VALID_DOI_A: quote(VALID_DOI_A),
    VALID_DOI_B: quote(VALID_DOI_B),
    VALID_DC_DOI: quote(VALID_DC_DOI),
    VALID_DC_DOI_A: quote(VALID_DC_DOI_A),
    VALID_DC_DOI_B: quote(VALID_DC_DOI_B),
    VALID_XR_DOI: quote(VALID_XR_DOI),
    VALID_XR_DOI_A: quote(VALID_XR_DOI_A),
    VALID_XR_DOI_B: quote(VALID_XR_DOI_B),
    INVALID_JSON: quote(INVALID_JSON),
    INVALID_XML: quote(INVALID_XML),
    NO_XML_NODE: quote(NO_XML_NODE),
}

SPACE_STR = "      \n\n   \t   "
INVALID_JSON_STR = '{"this": "that"'

DATACITE_URI = "https://api.datacite.org/dois"
CROSSREF_URI = "https://api.crossref.org/works"
OSTI_URI = "https://www.osti.gov/api/v1/records"

OK = "ok"
CODE = "status_code"
CONTENT = "content"
JSON = CE.JSON
ES = set()


DOI_FILE = {
    "INVALID": "tests/data/doi_files/doi_list_invalid.txt",
    "VALID": "tests/data/doi_files/doi_list_valid.txt",
    "VALID_INVALID": "tests/data/doi_files/doi_list_valid_invalid.txt",
    "XR_DC_VALID": "tests/data/doi_files/doi_list_xr_dc.txt",
    "XR_VALID": "tests/data/doi_files/doi_list_xr_valid.txt",
    "XR_VALID_INVALID": "tests/data/doi_files/doi_list_xr_valid_invalid.txt",
    "XR_INVALID": "tests/data/doi_files/doi_list_invalid.txt",
    "DC_VALID": "tests/data/doi_files/doi_list_dc_valid.txt",
    "DC_VALID_INVALID": "tests/data/doi_files/doi_list_dc_valid_invalid.txt",
    "DC_INVALID": "tests/data/doi_files/doi_list_invalid.txt",
}


# input for cleaning up DOI lists
TRIM_DEDUPE_LIST_DATA = [
    pytest.param(
        {
            "input": None,
            "output": ES,
        },
        id="None_input",
    ),
    pytest.param(
        {
            "input": VALID_DOI_A,
            "error": (
                "1 validation error for TrimDedupeList\n"
                "list_items\n  value is not a valid list (type=type_error.list)"
            ),
        },
        id="invalid_input_type",
    ),
    pytest.param(
        {
            "input": [],
            "output": ES,
        },
        id="zero_length_list_input",
    ),
    pytest.param(
        {
            "input": [""],
            "error": (
                "1 validation error for TrimDedupeList\n"
                "list_items -> 0\n"
                "  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="zero_str_length",
    ),
    pytest.param(
        {
            "input": [None, None],
            "error": (
                "2 validation errors for TrimDedupeList\n"
                "list_items -> 0\n  none is not an allowed value (type=type_error.none.not_allowed)\n"
                "list_items -> 1\n  none is not an allowed value (type=type_error.none.not_allowed)"
            ),
        },
        id="list_of_None",
    ),
    pytest.param(
        {
            "input": ["       ", "  \t  \n\n", ""],
            "error": (
                "3 validation errors for TrimDedupeList\n"
                "list_items -> 0\n"
                "  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)\n"
                "list_items -> 1\n"
                "  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)\n"
                "list_items -> 2\n"
                "  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)"
            ),
        },
        id="spaced_out",
    ),
    pytest.param(
        {
            "input": [10.12345, 12345, f"     {VALID_DOI_B}       "],
            "output": {"10.12345", "12345", VALID_DOI_B},
        },
        id="format_conversion",
    ),
    pytest.param(
        {
            "input": [
                f"  {VALID_DOI_A} ",
                f"\t\t\t{NOT_FOUND_DOI_B}\t\t\t",
                VALID_DOI_A,
                NOT_FOUND_DOI_B,
                f"   {VALID_DOI_A}\n\n",
            ],
            "output": {VALID_DOI_A, NOT_FOUND_DOI_B},
        },
        id="duplicates",
    ),
    pytest.param(
        {
            "input": [VALID_DOI_A, VALID_DOI_B, NOT_FOUND_DOI_B, NOT_FOUND_DOI_A],
            "output": {VALID_DOI_A, VALID_DOI_B, NOT_FOUND_DOI_B, NOT_FOUND_DOI_A},
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


FILE_LIST_TEST_DATA = [
    pytest.param(
        {"input": Path("tests") / "data" / "empty.txt", "output": set()},
        id="invalid_doi_file_empty",
    ),
    pytest.param(
        {"input": Path("tests") / "data" / "whitespace.txt", "output": set()},
        id="invalid_doi_file_whitespace",
    ),
    pytest.param(
        {
            "input": Path("tests") / "data" / "doi_files" / "doi_list_with_dupes.txt",
            "output": {
                '10.100/%"# ?.<>{}^[]`|\\+',
                "10.1000/12%34?56.78#90",
                "10.12345/†r05{2}?ef*(uri)",
                "10.12345/d@*c1t3.(uri)",
            },
        },
        id="valid_doi_file_dupes",
    ),
    pytest.param(
        {
            "input": Path("tests")
            / "data"
            / "doi_files"
            / "doi_list_valid_invalid.txt",
            "output": {VALID_DOI_A, VALID_DOI_B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B},
        },
        id="valid_doi_file_named_dois",
    ),
    pytest.param(
        {
            "input": "/does/not/exist",
            "error_type": FileNotFoundError,
            "error": "[Errno 2] No such file or directory: '/does/not/exist'",
        },
        id="invalid_doi_file_does_not_exist",
    ),
    pytest.param(
        {
            "input": "tests/data",
            "error_type": IsADirectoryError,
            "error": f"[Errno 21] Is a directory: '{full_path('tests/data')}'",
        },
        id="invalid_doi_file_directory",
    ),
]


DATA_FILES = {
    CE.DATACITE: {
        VALID_DOI_A: {
            CE.JSON: "sample_data/datacite/10.25585_1487552.json",
            CE.XML: "sample_data/datacite/10.25585_1487552.xml",
        },
        VALID_DOI_B: {
            CE.JSON: "sample_data/datacite/10.25585_1487554.json",
            CE.XML: "sample_data/datacite/10.25585_1487554.xml",
        },
        VALID_DC_DOI: {
            CE.JSON: "sample_data/datacite/10.25585_1487730.json",
            CE.XML: "sample_data/datacite/10.25585_14877730.xml",
        },
        VALID_DC_DOI_A: {
            CE.JSON: "sample_data/datacite/10.25982_90997.49_1783189.json",
            CE.XML: "sample_data/datacite/10.25982_90997.49_1783189.xml",
        },
        VALID_DC_DOI_B: {
            CE.JSON: "sample_data/datacite/10.25982_54100.27_1635639.json",
            CE.XML: "sample_data/datacite/10.25982_54100.27_1635639.xml",
        },
    },
    CE.CROSSREF: {
        VALID_DOI_A: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60007526.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_10.25585_60007526.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_10.25585_60007526.unixsd.xml",
        },
        VALID_DOI_B: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60007530.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_10.25585_60007530.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_10.25585_60007530.unixsd.xml",
        },
        VALID_XR_DOI: {
            CE.JSON: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixsd.xml",
        },
        VALID_XR_DOI_A: {
            CE.JSON: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixsd.xml",
        },
        VALID_XR_DOI_B: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60001190.json",
            CE.UNIXREF: "sample_data/crossref/10.46936_10.25585_60001190.unixref.xml",
            CE.UNIXSD: "sample_data/crossref/10.46936_10.25585_60001190.unixsd.xml",
        },
    },
    CE.OSTI: {
        VALID_DOI_A: {
            CE.JSON: "sample_data/osti/10.25982_1668075.json",
            CE.XML: "sample_data/osti/10.25982_1668075.xml",
        },
        VALID_DOI_B: {
            CE.JSON: "sample_data/osti/10.25982_1722943.json",
            CE.XML: "sample_data/osti/10.25982_1722943.xml",
        },
        VALID_DC_DOI_A: {
            CE.JSON: "sample_data/osti/10.25982_90997.49_1783189.json",
            CE.XML: "sample_data/osti/10.25982_90997.49_1783189.xml",
        },
        VALID_DC_DOI_B: {
            CE.JSON: "sample_data/osti/10.25982_54100.27_1635639.json",
            CE.XML: "sample_data/osti/10.25982_54100.27_1635639.xml",
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

    print(f"No response found for {source} {doi} {fmt}; returning None")
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
    f"{CROSSREF_URI}/{URI[VALID_DC_DOI]}/agency": {
        **OK_200,
        JSON: {"message": {"agency": {"id": "datacite"}}},
    },
    f"{CROSSREF_URI}/{URI[VALID_XR_DOI]}/agency": {
        **OK_200,
        JSON: {"message": {"agency": {"id": "crossref"}}},
    },
    f"{CROSSREF_URI}/{URI[INVALID_JSON]}": {
        **OK_200,
        CONTENT: INVALID_JSON_STR,
    },
    # crossref
    f"{CROSSREF_URI}/{URI[VALID_XR_DOI]}": {
        **OK_200,
        JSON: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI, CE.JSON),
    },
    # datacite
    f"{DATACITE_URI}/{URI[VALID_DC_DOI]}?affiliation=true": {
        **OK_200,
        JSON: generate_response_for_doi(CE.DATACITE, VALID_DC_DOI, CE.JSON),
    },
    f"{DATACITE_URI}/{URI[INVALID_JSON]}?affiliation=true": {
        **OK_200,
        CONTENT: INVALID_JSON_STR,
    },
    f"{DATACITE_URI}/{URI[NO_XML_NODE]}?affiliation=true": {
        **OK_200,
        JSON: {"this": "that"},
    },
    f"{DATACITE_URI}/{URI[INVALID_XML]}?affiliation=true": {
        **OK_200,
        JSON: {"data": {"attributes": {"xml": "abcdefghijklmopqrst"}}},
    },
    # osti
    f"{OSTI_URI}?doi={URI[INVALID_JSON]}": {
        **OK_200,
        CONTENT: INVALID_JSON_STR,
    },
    f"{OSTI_URI}?doi={URI[INVALID_XML]}": {
        **OK_200,
        CONTENT: "TODO",
    },
}

# JSON responses
for doi in [VALID_DOI_A, VALID_DOI_B, VALID_XR_DOI_A, VALID_XR_DOI_B]:
    # crossref retrieve_doi
    RESPONSE_DATA[f"{CROSSREF_URI}/{URI[doi]}"] = {
        **OK_200,
        JSON: generate_response_for_doi(CE.CROSSREF, doi, CE.JSON),
    }

# JSON responses
for doi in [VALID_DOI_A, VALID_DOI_B, VALID_DC_DOI_A, VALID_DC_DOI_B]:
    # datacite retrieve_doi
    RESPONSE_DATA[f"{DATACITE_URI}/{URI[doi]}?affiliation=true"] = {
        **OK_200,
        JSON: generate_response_for_doi(CE.DATACITE, doi, CE.JSON),
    }
    # osti
    RESPONSE_DATA[f"{OSTI_URI}?doi={URI[doi]}"] = {
        **OK_200,
        JSON: generate_response_for_doi(CE.OSTI, doi, CE.JSON),
    }

# crossref XML responses
for doi in [VALID_DOI_A, VALID_DOI_B, VALID_XR_DOI, VALID_XR_DOI_A, VALID_XR_DOI_B]:
    for fmt in [CE.UNIXREF, CE.UNIXSD]:
        RESPONSE_DATA[
            f"https://doi.crossref.org/servlet/query?id={URI[doi]}&format={fmt}&pid={QUOTED_DEFAULT_EMAIL}"
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
                for doi in [VALID_DOI_A, VALID_DOI_B, VALID_DC_DOI_A, VALID_DC_DOI_B]:
                    if kwargs["url"].find(URI[doi]) != -1:
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
