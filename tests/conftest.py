import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pytest
import requests
from pydantic import ValidationError, validate_arguments

import credit_engine.constants as CE  # noqa: N812  # noqa: N812
from credit_engine.clients import crossref, datacite, osti
from credit_engine.util import full_path

CWD: Path = full_path("")
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

DOI_FILE_INVALID = "tests/data/doi_files/doi_list_invalid.txt"
DOI_FILE = {
    "INVALID": DOI_FILE_INVALID,
    "VALID": "tests/data/doi_files/doi_list_valid.txt",
    "VALID_INVALID": "tests/data/doi_files/doi_list_valid_invalid.txt",
    "XR_DC_VALID": "tests/data/doi_files/doi_list_xr_dc.txt",
    "XR_VALID": "tests/data/doi_files/doi_list_xr_valid.txt",
    "XR_VALID_INVALID": "tests/data/doi_files/doi_list_xr_valid_invalid.txt",
    "XR_INVALID": DOI_FILE_INVALID,
    "DC_VALID": "tests/data/doi_files/doi_list_dc_valid.txt",
    "DC_VALID_INVALID": "tests/data/doi_files/doi_list_dc_valid_invalid.txt",
    "DC_INVALID": DOI_FILE_INVALID,
}


CLIENT = {
    CE.CROSSREF: crossref,
    CE.DATACITE: datacite,
    CE.OSTI: osti,
}

DOT_JSON = ".json"
DOT_XML = ".xml"

DATA_FORMAT = {
    CE.CROSSREF: {
        CE.OutputFormat.JSON: DOT_JSON,
        CE.OutputFormat.XML: DOT_XML,
    },
    CE.DATACITE: {
        CE.OutputFormat.JSON: DOT_JSON,
        CE.OutputFormat.XML: DOT_XML,
    },
    CE.OSTI: {
        CE.OutputFormat.JSON: DOT_JSON,
        CE.OutputFormat.XML: DOT_XML,
    },
    # CE.OSTI_ELINK: {
    #     CE.OutputFormat.JSON: DOT_JSON,
    #     CE.OutputFormat.XML: DOT_XML,
    # },
}

# validation errors
ERROR_NONE_NOT_ALLOWED = (
    "  none is not an allowed value (type=type_error.none.not_allowed)"
)
ERROR_AT_LEAST_ONE_ITEM = (
    "  ensure this value has at least 1 items "
    + "(type=value_error.set.min_items; limit_value=1)"
)
ERROR_AT_LEAST_THREE_CHARS = (
    "  ensure this value has at least 3 characters "
    + "(type=value_error.any_str.min_length; limit_value=3)"
)
ERROR_NOT_VALID_SET = "  value is not a valid set (type=type_error.set)"
ERROR_FIELD_REQUIRED = "  field required (type=value_error.missing)"

ERROR_VALUE_NOT_ENUM_MEMBER = (
    "  value is not a valid enumeration member; "
    "permitted: 'json', 'xml' "
    "(type=type_error.enum; enum_values="
    "[<OutputFormat.JSON: 'json'>, <OutputFormat.XML: 'xml'>])"
)

ERROR_NOT_A_BOOLEAN = "  value could not be parsed to a boolean (type=type_error.bool)"

DOI_LIST = "doi_list"

# input for cleaning up DOI lists
DOI_LIST_TEST_DATA = [
    pytest.param(
        {
            "args": {"doi_list": None},
            "output": None,
        },
        id="doi_list_valid_None",
    ),
    pytest.param(
        {
            "args": {"doi_list": VALID_DC_DOI_A},
            "error": [DOI_LIST + "\n" + ERROR_NOT_VALID_SET],
        },
        id="doi_list_invalid_str_input",
    ),
    pytest.param(
        {
            "args": {"doi_list": []},
            "output": None,
            "error": [DOI_LIST + "\n" + ERROR_AT_LEAST_ONE_ITEM],
        },
        id="doi_list_valid_0_len_list",
    ),
    pytest.param(
        {
            "args": {"doi_list": [""]},
            "error": [
                f"{DOI_LIST} -> 0\n" + ERROR_AT_LEAST_THREE_CHARS,
            ],
        },
        id="doi_list_invalid_0_len_str",
    ),
    pytest.param(
        {
            "args": {"doi_list": [None, None]},
            "error": [f"{DOI_LIST} -> 0\n" + ERROR_NONE_NOT_ALLOWED],
        },
        id="doi_list_invalid_list_of_None",
    ),
    pytest.param(
        {
            "args": {"doi_list": ["       ", "  \t  \n\n", ""]},
            "error": [
                f"{DOI_LIST} -> 0\n" + ERROR_AT_LEAST_THREE_CHARS,
                f"{DOI_LIST} -> 1\n" + ERROR_AT_LEAST_THREE_CHARS,
                f"{DOI_LIST} -> 2\n" + ERROR_AT_LEAST_THREE_CHARS,
            ],
        },
        id="doi_list_invalid_spaced_out",
    ),
    pytest.param(
        {
            "args": {"doi_list": [10.12345, 12345, f"     {VALID_DC_DOI_B}       "]},
            "output": {"10.12345", "12345", VALID_DC_DOI_B},
        },
        id="valid_dois_format_conversion",
    ),
    pytest.param(
        {
            "args": {
                "doi_list": [
                    f"  {VALID_XR_DOI_A} ",
                    f"\t\t\t{NOT_FOUND_DOI_B}\t\t\t",
                    VALID_XR_DOI_A,
                    NOT_FOUND_DOI_B,
                    f"   {VALID_XR_DOI_A}\n\n",
                ],
            },
            "output": {VALID_XR_DOI_A, NOT_FOUND_DOI_B},
        },
        id="valid_dois_duplicates",
    ),
    pytest.param(
        {
            "args": {
                "doi_list": [
                    VALID_XR_DOI_A,
                    VALID_XR_DOI_B,
                    NOT_FOUND_DOI_A,
                    NOT_FOUND_DOI_B,
                ]
            },
            "output": {
                VALID_XR_DOI_A,
                VALID_XR_DOI_B,
                NOT_FOUND_DOI_A,
                NOT_FOUND_DOI_B,
            },
        },
        id="valid_dois_all_ok",
    ),
    pytest.param(
        {
            "args": {"doi_list": ""},
            "error": [DOI_LIST + "\n" + ERROR_NOT_VALID_SET],
        },
        id="invalid_dois_empty_str",
    ),
    pytest.param(
        {
            "args": {"doi_list": {}},
            "error": [DOI_LIST + "\n" + ERROR_NOT_VALID_SET],
        },
        id="invalid_dois_dict_input",
    ),
    pytest.param(
        {"args": {}, "output": None},
        id="valid_dois_missing_input",
    ),
]

DOIS_FROM_FILE = "dois_from_file\n"
DOI_FILE_N = "doi_file\n"

FILE_CONTENTS_TEST_DATA = [
    pytest.param(
        {
            "args": {
                "doi_file": Path("tests")
                / "data"
                / "doi_files"
                / "doi_list_with_dupes.txt"
            },
            "output": {
                VALID_DOI_A,
                VALID_DOI_B,
                VALID_DC_DOI,
                VALID_XR_DOI,
            },
        },
        id="doi_file_valid_dupes",
    ),
    pytest.param(
        {
            "args": {
                "doi_file": Path("tests")
                / "data"
                / "doi_files"
                / "doi_list_dc_valid_invalid.txt",
            },
            "output": {
                VALID_DC_DOI_A,
                VALID_DC_DOI_B,
                NOT_FOUND_DOI_A,
                NOT_FOUND_DOI_B,
            },
        },
        id="doi_file_valid_named_dois",
    ),
    pytest.param(
        {
            "args": {"doi_file": Path("tests") / "data" / "empty.txt"},
            "error": [
                DOIS_FROM_FILE
                + "  No content found in "
                + str(full_path("tests/data/empty.txt"))
                + " (type=value_error)"
            ],
            "error_type": ValueError,
            "error_text": "No content found in tests/data/empty.txt",
        },
        id="doi_file_invalid_empty",
    ),
    pytest.param(
        {
            "args": {"doi_file": Path("tests") / "data" / "whitespace.txt"},
            "error": [
                DOIS_FROM_FILE
                + "  No content found in "
                + str(full_path("tests/data/whitespace.txt"))
                + " (type=value_error)"
            ],
            "error_type": ValueError,
            "error_text": "No content found in tests/data/whitespace.txt",
        },
        id="doi_file_invalid_whitespace",
    ),
    pytest.param(
        {
            "args": {"doi_file": "/does/not/exist"},
            "error": [
                DOI_FILE_N
                + '  file or directory at path "/does/not/exist" does not exist '
                + "(type=value_error.path.not_exists; path=/does/not/exist)"
            ],
            "error_type": FileNotFoundError,
            "error_text": "[Errno 2] No such file or directory: '/does/not/exist'",
        },
        id="doi_file_invalid_does_not_exist",
    ),
    pytest.param(
        {
            "args": {"doi_file": "tests/data"},
            "error": [
                DOI_FILE_N
                + '  path "'
                + str(CWD)
                + '/tests/data"'
                + " does not point to a file (type=value_error.path.not_a_file; path="
                + str(CWD)
                + "/tests/data)"
            ],
            "error_type": IsADirectoryError,
            "error_text": f"[Errno 21] Is a directory: '{full_path('tests/data')}'",
        },
        id="doi_file_invalid_directory",
    ),
    pytest.param(
        {
            "args": {"doi_file": "\n\n\t\r"},
            "error": [
                DOI_FILE_N
                + '  file or directory at path "'
                + str(CWD)
                + '/\n\n\t\r" does not exist '
                + "(type=value_error.path.not_exists; path="
                + str(CWD)
                + "/\n\n\t\r)"
            ],
            "error_type": FileNotFoundError,
            "error_text": f"[Errno 2] No such file or directory: '{CWD}/\\n\\n\\t\\r'",
        },
        id="doi_file_invalid_empty_string",
    ),
    pytest.param(
        {
            "args": {"doi_file": ""},
            "error": [
                DOI_FILE_N
                + '  path "'
                + str(CWD)
                + '" does not point to a file (type=value_error.path.not_a_file; path='
                + str(CWD)
                + ")"
            ],
            "error_type": IsADirectoryError,
            "error_text": f"[Errno 21] Is a directory: '{CWD}'",
        },
        id="doi_file_invalid_empty_string_current_dir",
    ),
    pytest.param(
        {
            "args": {"doi_file": None},
            "error": ["doi_file -> file_path\n" + ERROR_NONE_NOT_ALLOWED],
            "error_type": ValidationError,
            "error_text": ERROR_NONE_NOT_ALLOWED,
        },
        id="doi_file_invalid_None",
    ),
    pytest.param(
        {
            "args": {},
            "output": set(),
            "error_type": ValidationError,
            "error_text": "file_path\n" + ERROR_FIELD_REQUIRED,
        },
        id="doi_file_valid_missing",
    ),
]


SOURCE_TEST_DATA = [
    pytest.param(
        {
            "args": {},
            "error": "Missing required parameter: source",
        },
        id="source_invalid_missing",
    ),
    pytest.param(
        {
            "args": {"source": None},
            "error": "Invalid data source: None",
        },
        id="source_invalid_None",
    ),
    pytest.param(
        {
            "args": {"source": ""},
            "error": "Invalid data source: ''",
        },
        id="source_invalid_empty",
    ),
    pytest.param(
        {
            "args": {"source": "      \n\r\t  "},
            "error": "Invalid data source: '      \\n\\r\\t  '",
        },
        id="source_invalid_whitespace",
    ),
    pytest.param(
        {
            "args": {"source": "THE BOWELS OF HELL"},
            "error": "Invalid data source: 'THE BOWELS OF HELL'",
        },
        id="source_invalid_string",
    ),
    pytest.param(
        {
            "args": {"source": 12345},
            "error": "Invalid data source: 12345",
        },
        id="source_invalid_type_error_int",
    ),
    pytest.param(
        {
            "args": {"source": [1, 2, 3, 4]},
            "error": "Invalid data source: [1, 2, 3, 4]",
        },
        id="source_invalid_type_error_list",
    ),
    pytest.param(
        {
            "args": {"source": CE.OSTI},
            "output": osti,
        },
        id="source_valid",
    ),
]


OUTPUT_FORMATS = "output_formats\n"

ERROR_OUTPUT_FORMATS_INVALID = "  Invalid output format(s): "
ERROR_OUTPUT_FORMATS_VALID = (
    "\n  Valid output formats: OutputFormat.JSON, OutputFormat.XML (type=value_error)"
)
ERROR_OUTPUT_FORMATS_VALID_JSON_ONLY = (
    "\n  Valid output formats: OutputFormat.JSON (type=value_error)"
)

OUTPUT_FORMATS_TEST_DATA = [
    pytest.param(
        {
            "args": {
                "output_formats": "txt",
            },
            "error": [OUTPUT_FORMATS + ERROR_NOT_VALID_SET],
        },
        id="fmt_invalid_type_str",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": ["", "", ""],
            },
            "error": [
                OUTPUT_FORMATS
                + ERROR_OUTPUT_FORMATS_INVALID
                + "''"
                + ERROR_OUTPUT_FORMATS_VALID,
            ],
        },
        id="fmt_invalid_list_of_empties",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": ["        ", "\n\n     \r  \t ", "\r\n"],
            },
            "error": [
                OUTPUT_FORMATS
                + ERROR_OUTPUT_FORMATS_INVALID
                + "'        ', '\\n\\n     \\r  \\t ', '\\r\\n'"
                + ERROR_OUTPUT_FORMATS_VALID,
            ],
        },
        id="fmt_invalid_list_of_empty_strings",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {None},
            },
            "error": [
                OUTPUT_FORMATS
                + ERROR_OUTPUT_FORMATS_INVALID
                + "None"
                + ERROR_OUTPUT_FORMATS_VALID,
            ],
        },
        id="fmt_invalid_set_of_None",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {"text"},
            },
            "error": [
                OUTPUT_FORMATS
                + ERROR_OUTPUT_FORMATS_INVALID
                + "'text'"
                + ERROR_OUTPUT_FORMATS_VALID,
            ],
        },
        id="fmt_invalid_value",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": ["rdfxml", CE.XML, CE.JSON, "duck types"],
            },
            "error": [
                OUTPUT_FORMATS
                + ERROR_OUTPUT_FORMATS_INVALID
                + "'duck types', 'rdfxml'"
                + ERROR_OUTPUT_FORMATS_VALID,
            ],
        },
        id="fmt_invalid_values",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {CE.JSON},
            },
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_valid_JSON",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": [
                    CE.OutputFormat.JSON,
                    CE.OutputFormat.JSON,
                    CE.OutputFormat.JSON,
                    "jSON",
                    "json",
                    "Json",
                ],
            },
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_valid_list_output_format_JSON_dupes",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {"json"},
            },
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_valid_JSON_str_lc",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {"JSON"},
            },
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_valid_JSON_str_uc",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {"jSoN"},
            },
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_valid_JSON_str_leet",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {" \n\n jSoN  \r\n \t "},
            },
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_valid_JSON_str_spacy",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {"json", CE.XML},
            },
            "output": {CE.OutputFormat.JSON, CE.OutputFormat.XML},
        },
        id="fmt_valid_JSON_str_XML_abbr",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": {
                    CE.JSON,
                    CE.OutputFormat.XML,
                    "    json  ",
                    "\n\nXML\n\n",
                    "JSON",
                    "XML",
                },
            },
            "output": {CE.OutputFormat.JSON, CE.OutputFormat.XML},
        },
        id="fmt_valid_misc_json_xml",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": "",
            },
            "error": [OUTPUT_FORMATS + ERROR_NOT_VALID_SET],
        },
        id="fmt_invalid_0-len_string",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": "     ",
            },
            "error": [OUTPUT_FORMATS + ERROR_NOT_VALID_SET],
        },
        id="fmt_invalid_spaces",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": "something invalid",
            },
            "error": [OUTPUT_FORMATS + ERROR_NOT_VALID_SET],
        },
        id="fmt_invalid_invalid_text",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": [],
            },
            "error": [OUTPUT_FORMATS + ERROR_AT_LEAST_ONE_ITEM],
        },
        id="fmt_invalid_empty_list",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": ES,
            },
            "error": [OUTPUT_FORMATS + ERROR_AT_LEAST_ONE_ITEM],
        },
        id="fmt_invalid_empty_set",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": object(),
            },
            "error": [OUTPUT_FORMATS + ERROR_NOT_VALID_SET],
        },
        id="fmt_invalid_object",
    ),
    pytest.param(
        {
            "args": {
                "output_formats": None,
            },
            "error": [
                OUTPUT_FORMATS + ERROR_NONE_NOT_ALLOWED,
            ],
        },
        id="fmt_invalid_None",
    ),
    pytest.param(
        {
            "args": {},
            "output": {CE.OutputFormat.JSON},
        },
        id="fmt_missing_use_default",
    ),
]

SOURCE_X_FORMAT_TEST_DATA = []

# JSON + XML
for src in [CE.CROSSREF, CE.DATACITE]:
    src_fmt_test_data = [
        pytest.param(
            {
                "args": {
                    "output_formats": {
                        CE.JSON,
                        CE.OutputFormat.XML,
                        "    json  ",
                        "\n\nXML\n\n",
                        "JSON",
                        "XML",
                    },
                    "source": src,
                },
                "output": {CE.OutputFormat.JSON, CE.OutputFormat.XML},
            },
            id=f"{src}_fmt_valid_misc_json_xml",
        ),
        pytest.param(
            {
                "args": {
                    "output_formats": ["rdfxml", CE.XML, CE.JSON, "duck types"],
                    "source": src,
                },
                "error": [
                    OUTPUT_FORMATS
                    + ERROR_OUTPUT_FORMATS_INVALID
                    + "'duck types', 'rdfxml'"
                    + ERROR_OUTPUT_FORMATS_VALID,
                ],
            },
            id=f"{src}_fmt_invalid_values",
        ),
    ]
    SOURCE_X_FORMAT_TEST_DATA = SOURCE_X_FORMAT_TEST_DATA + src_fmt_test_data


for src in []:  # CE.OSTI]:
    src_fmt_test_data = [
        pytest.param(
            {
                "args": {
                    "output_formats": {
                        CE.JSON,
                        CE.OutputFormat.XML,
                        "    json  ",
                        "\n\nXML\n\n",
                        "JSON",
                        "XML",
                    },
                    "source": src,
                },
                "error": [
                    OUTPUT_FORMATS
                    + ERROR_OUTPUT_FORMATS_INVALID
                    + "OutputFormat.XML"
                    + ERROR_OUTPUT_FORMATS_VALID_JSON_ONLY,
                ],
            },
            id=f"{src}_fmt_invalid_misc_json_xml",
        ),
        pytest.param(
            {
                "args": {
                    "output_formats": ["rdfxml", CE.XML, CE.JSON, "duck types"],
                    "source": src,
                },
                "error": [
                    OUTPUT_FORMATS
                    + ERROR_OUTPUT_FORMATS_INVALID
                    + "'duck types', 'rdfxml', OutputFormat.XML"
                    + ERROR_OUTPUT_FORMATS_VALID_JSON_ONLY,
                ],
            },
            id=f"{src}_fmt_invalid_values",
        ),
    ]

    SOURCE_X_FORMAT_TEST_DATA = SOURCE_X_FORMAT_TEST_DATA + src_fmt_test_data

for src in [CE.CROSSREF, CE.DATACITE, CE.OSTI]:
    SOURCE_X_FORMAT_TEST_DATA = [
        *SOURCE_X_FORMAT_TEST_DATA,
        pytest.param(
            {
                "args": {"source": src},
                "output": {CE.OutputFormat.JSON},
            },
            id=f"{src}_fmt_missing_use_default",
        ),
        pytest.param(
            {
                "args": {"source": src, "output_formats": {CE.OutputFormat.JSON}},
                "output": {CE.OutputFormat.JSON},
            },
            id=f"{src}_fmt_json",
        ),
        pytest.param(
            {
                "args": {"output_formats": None, "source": src},
                "error": [
                    OUTPUT_FORMATS + ERROR_NONE_NOT_ALLOWED,
                ],
            },
            id=f"{src}_fmt_invalid_None",
        ),
    ]


save_files_proto_data = [
    (
        {
            "args": {
                "save_dir": CWD,
            },
            "output": False,
        },
        "valid_missing",
    ),
    (
        {
            "args": {
                "save_files": "true",
                "save_dir": CWD,
            },
            "output": True,
        },
        "valid_string",
    ),
    (
        {
            "args": {
                "save_files": True,
                "save_dir": CWD,
            },
            "output": True,
        },
        "valid_bool",
    ),
    (
        {
            "args": {
                "save_files": "",
                "save_dir": CWD,
            },
            "error": ["save_files\n" + ERROR_NOT_A_BOOLEAN],
        },
        "invalid_empty",
    ),
    (
        {
            "args": {
                "save_files": None,
                "save_dir": CWD,
            },
            "output": False,
        },
        "valid_None",
    ),
    (
        {
            "args": {
                "save_files": 12345,
                "save_dir": CWD,
            },
            "error": ["save_files\n" + ERROR_NOT_A_BOOLEAN],
        },
        "invalid_integers",
    ),
]

SAVE_FILES_TEST_DATA = [
    pytest.param(item[0], id=f"save_files_{item[1]}") for item in save_files_proto_data
]

SAVE_DIR_N = "save_dir\n"
save_dir_proto_data = [
    (
        {
            "args": {
                "save_dir": "/does/not/exist",
            },
            "error": [
                SAVE_DIR_N
                + '  file or directory at path "/does/not/exist" does not exist '
                + "(type=value_error.path.not_exists; path=/does/not/exist)"
            ],
        },
        "invalid_abs",
    ),
    (
        {
            "args": {
                "save_dir": "does/not/exist",
            },
            "error": [
                SAVE_DIR_N
                + '  file or directory at path "'
                + str(CWD)
                + '/does/not/exist" does not exist '
                + "(type=value_error.path.not_exists; path="
            ],
        },
        "invalid_rel",
    ),
    (
        {
            "args": {
                "save_dir": "CHANGELOG.md",
            },
            "error": [
                SAVE_DIR_N
                + '  path "'
                + str(CWD)
                + '/CHANGELOG.md" does not point to a directory '
                + "(type=value_error.path.not_a_directory; path="
            ],
        },
        "invalid_file",
    ),
    (
        {
            "args": {
                "save_dir": None,
            },
            "error": [SAVE_DIR_N + "  save_dir must be defined if save_files is true"],
        },
        "invalid_none",
    ),
    (
        {
            "args": {},
            "error": [SAVE_DIR_N + "  save_dir must be defined if save_files is true"],
        },
        "invalid_missing",
    ),
    (
        {
            "args": {
                "save_dir": CWD,
            },
            "output": CWD,
        },
        "valid_cwd",
    ),
]

SAVE_DIR_TEST_DATA = [
    pytest.param(item[0], id=f"save_dir_{item[1]}") for item in save_dir_proto_data
]

save_files_abbrev_proto_data = [
    (
        {
            "args": {
                "save_files": "",
            },
            "error": ["save_files\n" + ERROR_NOT_A_BOOLEAN],
        },
        "invalid_empty",
    ),
    (
        {
            "args": {
                "save_files": None,
            },
            "output": False,
        },
        "valid_None",
    ),
    (
        {
            "args": {
                "save_files": True,
            },
            "output": True,
        },
        "valid_bool",
    ),
]

save_dir_x_save_files_proto_data = []
for save_dir_params in save_dir_proto_data:
    for save_files_params in save_files_abbrev_proto_data:
        (sf_params, sf_name) = save_files_params
        (sd_params, sd_name) = save_dir_params

        args = {}
        if "save_files" in sf_params["args"]:
            args["save_files"] = sf_params["args"]["save_files"]
        if "save_dir" in sd_params["args"]:
            args["save_dir"] = sd_params["args"]["save_dir"]

        if "output" in sf_params and sf_params["output"] is False:
            save_dir_x_save_files_proto_data.append(
                # pytest.param
                (
                    {
                        "args": args,
                        "output": {"save_dir": None, "save_files": False},
                    },
                    f"save_files_{sf_name}_save_dir_{sd_name}",
                )
            )
            continue

        if "error" in sf_params:
            save_dir_x_save_files_proto_data.append(
                # pytest.param
                (
                    {"args": args, "error": sf_params["error"]},
                    f"save_files_{sf_name}_save_dir_{sd_name}",
                )
            )
            continue

        params = {
            "args": args,
        }

        if "error" in sd_params:
            params["error"] = sd_params["error"]
        else:
            params["output"] = {
                "save_dir": sd_params["output"],
                "save_files": sf_params["output"],
            }

        save_dir_x_save_files_proto_data.append(
            (params, f"save_files_{sf_name}_save_dir_{sd_name}")
        )

SAVE_DIR_X_SAVE_FILES_TEST_DATA = [
    pytest.param(item[0], id=item[1]) for item in save_dir_x_save_files_proto_data
]

OUTPUT_FORMAT_EXT_TEST_DATA = [
    pytest.param(
        {
            "input": "Json",
            "output_format": CE.OutputFormat.JSON,
            "output_ext": DOT_JSON,
        },
        id="Json",
    ),
    pytest.param(
        {
            "input": "XmL",
            "output_format": CE.OutputFormat.XML,
            "output_ext": DOT_XML,
        },
        id="XmL",
    ),
    pytest.param(
        {
            "input": CE.JSON,
            "output_format": CE.OutputFormat.JSON,
            "output_ext": DOT_JSON,
        },
        id="CE.JSON",
    ),
    pytest.param(
        {
            "input": CE.XML,
            "output_format": CE.OutputFormat.XML,
            "output_ext": DOT_XML,
        },
        id="CE.XML",
    ),
    pytest.param(
        {
            "input": CE.OutputFormat.JSON,
            "output_format": CE.OutputFormat.JSON,
            "output_ext": DOT_JSON,
        },
        id="CE.OutputFormat.JSON",
    ),
    pytest.param(
        {
            "input": CE.OutputFormat.XML,
            "output_format": CE.OutputFormat.XML,
            "output_ext": DOT_XML,
        },
        id="CE.OutputFormat.XML",
    ),
    pytest.param(
        {
            "input": None,
            "error": ValidationError,
            "error_msg": re.escape(
                "1 validation error for GetExtension\nfmt\n" + ERROR_NONE_NOT_ALLOWED
            ),
            "errors": 'Invalid output format: "None"',
        },
        id="None",
    ),
    pytest.param(
        {
            "input": "",
            "error": ValueError,
            "error_msg": 'Invalid output format: ""',
        },
        id="0-len string",
    ),
    pytest.param(
        {
            "input": "     ",
            "error": ValueError,
            "error_msg": 'Invalid output format: "     "',
        },
        id="spaces",
    ),
    pytest.param(
        {
            "input": "something invalid",
            "error": ValueError,
            "error_msg": 'Invalid output format: "something invalid"',
        },
        id="invalid text",
    ),
]


# assumed argument input order:
# doi, output_format
GET_ENDPOINT_ONE_ERROR = "1 validation error for RetrieveOstiDoiArgs\n"
GET_ENDPOINT_ERRORS = " validation errors for RetrieveOstiDoiArgs\n"
ERROR_DOI = "doi\n"
ERROR_OUTPUT_FORMAT = "output_format\n"
ERROR_QUERY_DOI = "query -> doi\n"
OUTPUT_FORMAT_NOT_VALID_ENUM = ERROR_OUTPUT_FORMAT + ERROR_VALUE_NOT_ENUM_MEMBER


GET_ENDPOINT_FAIL_DATA = [
    pytest.param(
        {
            "input": {},
            "error": re.escape(
                GET_ENDPOINT_ONE_ERROR + ERROR_DOI + ERROR_FIELD_REQUIRED
            ),
        },
        id="no_args",
    ),
    pytest.param(
        {
            "input": {"doi": None},
            "error": re.escape(
                GET_ENDPOINT_ONE_ERROR + ERROR_DOI + ERROR_NONE_NOT_ALLOWED
            ),
        },
        id="doi_None",
    ),
    pytest.param(
        {
            "input": {"doi": ""},
            "error": re.escape(
                GET_ENDPOINT_ONE_ERROR + ERROR_DOI + ERROR_AT_LEAST_THREE_CHARS
            ),
        },
        id="doi_len_0",
    ),
    pytest.param(
        {
            "input": {"doi": SPACE_STR},
            "error": re.escape(
                GET_ENDPOINT_ONE_ERROR + ERROR_DOI + ERROR_AT_LEAST_THREE_CHARS
            ),
        },
        id="doi_whitespace",
    ),
    pytest.param(
        {
            "input": {"doi": "", "output_format": ""},
            "error": re.escape(
                "2"
                + GET_ENDPOINT_ERRORS
                + ERROR_DOI
                + ERROR_AT_LEAST_THREE_CHARS
                + OUTPUT_FORMAT_NOT_VALID_ENUM
            ),
            "error_dict": re.escape(
                "2"
                + GET_ENDPOINT_ERRORS
                + ERROR_QUERY_DOI
                + ERROR_AT_LEAST_THREE_CHARS
                + OUTPUT_FORMAT_NOT_VALID_ENUM
            ),
        },
        id="doi_len_0_fmt_len_0",
    ),
    pytest.param(
        {
            "input": {"doi": SPACE_STR, "output_format": SPACE_STR},
            "error": re.escape(
                "2"
                + GET_ENDPOINT_ERRORS
                + ERROR_DOI
                + ERROR_AT_LEAST_THREE_CHARS
                + OUTPUT_FORMAT_NOT_VALID_ENUM
            ),
            "error_dict": re.escape(
                "2"
                + GET_ENDPOINT_ERRORS
                + ERROR_QUERY_DOI
                + ERROR_AT_LEAST_THREE_CHARS
                + OUTPUT_FORMAT_NOT_VALID_ENUM
            ),
        },
        id="doi_whitespace_fmt_whitespace",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": None},
            "error": re.escape(
                GET_ENDPOINT_ONE_ERROR + ERROR_OUTPUT_FORMAT + ERROR_NONE_NOT_ALLOWED
            ),
        },
        id="fmt_none",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": ""},
            "error": re.escape(GET_ENDPOINT_ONE_ERROR + OUTPUT_FORMAT_NOT_VALID_ENUM),
        },
        id="fmt_len_0",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": SPACE_STR},
            "error": re.escape(GET_ENDPOINT_ONE_ERROR + OUTPUT_FORMAT_NOT_VALID_ENUM),
        },
        id="fmt_whitespace",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": "TXT"},
            "error": re.escape(GET_ENDPOINT_ONE_ERROR + OUTPUT_FORMAT_NOT_VALID_ENUM),
        },
        id="fmt_invalid",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": "JSON"},
            "error": re.escape(GET_ENDPOINT_ONE_ERROR + OUTPUT_FORMAT_NOT_VALID_ENUM),
        },
        id="fmt_str_uppercase",
    ),
    pytest.param(
        {
            "input": {"doi": SAMPLE_DOI, "output_format": "Json"},
            "error": re.escape(GET_ENDPOINT_ONE_ERROR + OUTPUT_FORMAT_NOT_VALID_ENUM),
        },
        id="fmt_str_titlecase",
    ),
]


# API response mocks below

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
            CE.XML: "sample_data/crossref/10.46936_10.25585_60007526.unixsd.xml",
        },
        VALID_DOI_B: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60007530.json",
            CE.XML: "sample_data/crossref/10.46936_10.25585_60007530.unixsd.xml",
        },
        VALID_XR_DOI: {
            CE.JSON: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.json",
            CE.XML: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixsd.xml",
        },
        VALID_XR_DOI_A: {
            CE.JSON: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.json",
            CE.XML: "sample_data/crossref/10.46936_jejc.proj.2013.48086_60005298.unixsd.xml",
        },
        VALID_XR_DOI_B: {
            CE.JSON: "sample_data/crossref/10.46936_10.25585_60001190.json",
            CE.XML: "sample_data/crossref/10.46936_10.25585_60001190.unixsd.xml",
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


def generate_response(file_path: str) -> None | bytes | str | list | dict:
    """Retrieve an API response from a file.

    :param file_path: file path
    :type file_path: str
    :return: data structure or string
    :rtype: None | bytes | str | list | dict
    """
    current_dir = Path.cwd()
    path_to_file = Path.resolve(current_dir.joinpath(Path(file_path)))
    if path_to_file.suffix == f".{CE.JSON}":
        with open(path_to_file, encoding="utf-8") as fh:
            return json.load(fh)

    return path_to_file.read_bytes()


@validate_arguments
def generate_response_for_doi(
    source: str, doi: str, fmt: str
) -> None | bytes | str | list | dict:
    """Generate a response for a given DOI.

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
    RESPONSE_DATA[
        f"https://doi.crossref.org/servlet/query?format=unixsd&id={URI[doi]}&pid={QUOTED_DEFAULT_EMAIL}"
    ] = {
        **OK_200,
        CONTENT: generate_response_for_doi(CE.CROSSREF, doi, CE.XML),
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
                for valid_id in [
                    VALID_DOI_A,
                    VALID_DOI_B,
                    VALID_DC_DOI_A,
                    VALID_DC_DOI_B,
                ]:
                    if kwargs["url"].find(URI[valid_id]) != -1:
                        self.response = {
                            **OK_200,
                            CONTENT: generate_response_for_doi(
                                CE.OSTI, valid_id, CE.XML
                            ),
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

    def json(self) -> list | dict:
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
    """Requests.get() returns a MockResponse object."""

    def mock_get(url: str, params: dict | None = None, **kwargs: dict | None):
        if params is None:
            params = {}
        response_args = {**params, **kwargs}

        if url:
            response_args["url"] = url
        return MockResponse(response_args)

    monkeypatch.setattr(requests, "get", mock_get)
