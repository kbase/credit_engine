import copy
import tempfile
from pathlib import Path

import pytest

import credit_engine.constants as CE
import tests.common as common
from credit_engine.clients import base, crossref, datacite, osti
from credit_engine.errors import make_error
from tests.conftest import (
    DOI_FILE,
    FILE_LIST_TEST_DATA,
    FILE_NAME,
    NOT_FOUND_DOI_A,
    NOT_FOUND_DOI_B,
    TRIM_DEDUPE_LIST_DATA,
    VALID_DC_DOI,
    VALID_DC_DOI_A,
    VALID_DC_DOI_B,
    VALID_XR_DOI,
    VALID_XR_DOI_A,
    VALID_XR_DOI_B,
    generate_response_for_doi,
)

CLIENT = {
    CE.CROSSREF: crossref,
    CE.DATACITE: datacite,
    CE.OSTI: osti,
}

INVALID_DOI_FILE = "tests/data/invalid_dois.txt"
VALID_DOI_FILE = "tests/data/valid_dois.txt"
VALID_AND_INVALID_DOI_FILE = "tests/data/valid_and_invalid.txt"
XR_DC_DOI_FILE = "tests/data/xr_dc.txt"


SOURCE_TEST_DATA = [pytest.param(src, id=src) for src in CLIENT]

DOT_JSON = ".json"
DOT_XML = ".xml"

DATA_FORMAT = {
    CE.CROSSREF: {
        CE.JSON: DOT_JSON,
        CE.XML: DOT_XML,
    },
    CE.DATACITE: {
        CE.JSON: DOT_JSON,
        CE.XML: DOT_XML,
    },
    CE.OSTI: {
        CE.JSON: DOT_JSON,
        CE.XML: DOT_XML,
    },
}


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


GET_EXTENSION_TEST_DATA = [
    pytest.param(
        {
            "client": datacite,
            "output_format": "JSON",
            "expected": datacite.FILE_EXTENSIONS[CE.JSON],
        },
        id="datacite_json",
    ),
    pytest.param(
        {
            "client": crossref,
            "output_format": CE.JSON,
            "expected": crossref.FILE_EXTENSIONS[CE.JSON],
        },
        id="crossref_json",
    ),
    pytest.param(
        {
            "client": osti,
            "output_format": "Json",
            "expected": osti.FILE_EXTENSIONS[CE.JSON],
        },
        id="osti_json",
    ),
    pytest.param(
        {
            "client": crossref,
            "output_format": CE.XML,
            "expected": crossref.FILE_EXTENSIONS[CE.XML],
        },
        id="crossref_xml",
    ),
    pytest.param(
        {
            "client": datacite,
            "output_format": "  XmL  \r",
            "expected": datacite.FILE_EXTENSIONS[CE.XML],
        },
        id="datacite_xml",
    ),
    pytest.param(
        {
            "client": osti,
            "output_format": "XML",
            "expected": osti.FILE_EXTENSIONS[CE.XML],
        },
        id="osti_xml",
    ),
]

# test data for retrieve_doi_list

INVALID_SOURCE_TEST_DATA = [
    pytest.param(
        {
            "input": "THE BOWELS OF HELL",
            "error": make_error(
                "invalid_param",
                {"param": CE.DATA_SOURCE, CE.DATA_SOURCE: "THE BOWELS OF HELL"},
            ),
        },
        id="invalid_source_string",
    ),
    pytest.param(
        {
            "input": "",
            "error": make_error(
                "invalid_param", {"param": CE.DATA_SOURCE, CE.DATA_SOURCE: ""}
            ),
        },
        id="invalid_source_empty",
    ),
    pytest.param(
        {
            "input": None,
            "error": make_error(
                "invalid_param", {"param": CE.DATA_SOURCE, CE.DATA_SOURCE: None}
            ),
        },
        id="invalid_source_None",
    ),
    pytest.param(
        {
            "input": CE.DATACITE,
        },
        id="valid_source",
    ),
]

OUTPUT_FORMAT_LIST = [
    # valid for Crossref, Datacite, OSTI
    pytest.param([CE.JSON], id="json"),
    pytest.param([CE.XML], id="xml"),
    pytest.param([CE.JSON, CE.XML], id="json_xml"),
    pytest.param(
        [CE.JSON, CE.XML, CE.JSON, CE.JSON, CE.XML, CE.XML],
        id="json_xml_duplicated_fmts",
    ),
]


INVALID_OUTPUT_FORMAT_LIST_TEST_DATA = [
    pytest.param(
        {
            "input": "txt",
            "error": make_error(
                "invalid_param", {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: "txt"}
            ),
        },
        id="invalid_fmt_type",
    ),
    pytest.param(
        {
            "input": [None, ""],
            "error": make_error(
                "invalid_param",
                {
                    "param": CE.OUTPUT_FORMAT,
                    CE.OUTPUT_FORMAT: [None, ""],
                },
            ),
        },
        id="invalid_fmt_list_of_empties",
    ),
    pytest.param(
        {
            "input": ["text"],
            "error": make_error(
                "invalid_param", {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: ["text"]}
            ),
        },
        id="invalid_fmt_value",
    ),
    pytest.param(
        {
            "input": ["rdfxml", CE.XML, CE.JSON, "duck types"],
            "error": make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: ["rdfxml", "duck types"]},
            ),
        },
        id="invalid_fmt_values",
    ),
    pytest.param(
        {
            "input": [CE.JSON],
        },
        id="valid_fmt",
    ),
    pytest.param(
        {
            "input": None,
        },
        id="valid_fmt_None_default",
    ),
]

INVALID_SAVE_DIR_TEST_DATA = [
    pytest.param(
        {
            "input": "/does/not/exist",
            "error": "invalid save_dir: '/does/not/exist' does not exist or is not a directory",
        },
        id="invalid_save_dir_abs",
    ),
    pytest.param(
        {
            "input": "does/not/exist",
            "error": "invalid save_dir: 'does/not/exist' does not exist or is not a directory",
        },
        id="invalid_save_dir_rel",
    ),
    pytest.param(
        {
            "input": "",
        },
        id="valid_save_dir",
    ),
]

SAVE_PARAMS = [
    pytest.param({"id": "no_save_no_dir"}, id="no_save_no_dir"),
    pytest.param(
        {
            "id": "no_save",
            "save_files": False,
            "save_dir": "tmp_path",
        },
        id="no_save",
    ),
    pytest.param(
        {
            "id": "save_to_default_dir",
            "save_files": True,
        },
        id="save_to_default_dir",
    ),
    pytest.param(
        {
            "id": "save_to_dir",
            "save_files": True,
            "save_dir": "tmp_path",
        },
        id="save_to_dir",
    ),
]


A = "a"
B = "b"
DOI_INPUT_TEST_DATA = [
    pytest.param(
        {
            "doi_list": [A, B],
            "all_dois": [A, B],
        },
        id="list_all_valid",
    ),
    pytest.param(
        {
            "doi_list": [A, NOT_FOUND_DOI_B],
            "all_dois": [A, NOT_FOUND_DOI_B],
        },
        id="list_some_valid",
    ),
    pytest.param(
        {
            "doi_list": [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
            "all_dois": [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
        },
        id="list_all_invalid",
    ),
    pytest.param(
        {
            "doi_file": "VALID_INVALID",
            "all_dois": [A, B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
        },
        id="file_some_valid",
    ),
    pytest.param(
        {
            "doi_list": [A, B],
            "doi_file": "INVALID",
            "all_dois": [A, B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
        },
        id="list_valid_file_invalid",
    ),
    pytest.param(
        {
            "doi_list": [A, NOT_FOUND_DOI_B],
            "doi_file": "VALID",
            "all_dois": [A, B, NOT_FOUND_DOI_B],
        },
        id="mixed_sources",
    ),
]
# mappings of A and B to the appropriate Crossref or Datacite DOI
TR_NOT_FOUND_DOI = {
    NOT_FOUND_DOI_A: NOT_FOUND_DOI_A,
    NOT_FOUND_DOI_B: NOT_FOUND_DOI_B,
}
TRANSLATED_DOI = {
    # True = crossref DOI, False = datacite DOI
    True: {A: VALID_XR_DOI_A, B: VALID_XR_DOI_B, **TR_NOT_FOUND_DOI},
    False: {A: VALID_DC_DOI_A, B: VALID_DC_DOI_B, **TR_NOT_FOUND_DOI},
}


@pytest.mark.parametrize("param", CHECK_DOI_SOURCE_TEST_DATA)
def test_check_doi_source(param, _mock_response):
    """Test the DOI source function

    :param param: doi: the DOI to query; expected: expected result
    :type param: pytest.param
    :param _mock_response: mock requests.get function
    :type _mock_response: pytest mock
    """
    assert base.check_doi_source(param["doi"]) == param["expected"]


def test_get_extension_fail_bad_source():
    SOURCE = "not a real source"
    error_text = f"No client for source {SOURCE}"
    with pytest.raises(ValueError, match=error_text):
        base.get_extension(SOURCE, CE.JSON)


@pytest.mark.parametrize("output_format", [CE.JSON, CE.XML])
@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
def test_get_extension(source, output_format):
    expected = DATA_FORMAT.get(source, {}).get(output_format)
    if expected is None:
        error_text = make_error(
            "invalid_param",
            {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
        )
        with pytest.raises(ValueError, match=error_text):
            base.get_extension(source, output_format)

    else:
        assert base.get_extension(source, output_format) == expected
        assert base.get_extension(source, output_format.upper()) == expected
        assert base.get_extension(source, output_format.title()) == expected
        assert base.get_extension(source, output_format.title().swapcase()) == expected


@pytest.mark.parametrize("doi_list", TRIM_DEDUPE_LIST_DATA)
@pytest.mark.parametrize("doi_file", FILE_LIST_TEST_DATA)
def test__validate_dois(doi_file, doi_list):
    all_dois = set()
    if "output" in doi_file:
        all_dois = set(doi_file["output"])
    if "output" in doi_list:
        all_dois = all_dois | set(doi_list["output"])

    error_list = []
    if "error" in doi_file:
        error_list.append(doi_file["error"])
    if "error" in doi_list:
        error_list.append(doi_list["error"])

    input_errors = []
    output = base._validate_dois(
        doi_file=doi_file["input"],
        doi_list=doi_list["input"],
        input_errors=input_errors,
    )

    assert set(output) == all_dois
    assert input_errors == error_list


@pytest.mark.parametrize("output_format_list", INVALID_OUTPUT_FORMAT_LIST_TEST_DATA)
@pytest.mark.parametrize("save_dir", INVALID_SAVE_DIR_TEST_DATA)
@pytest.mark.parametrize("source", INVALID_SOURCE_TEST_DATA)
@pytest.mark.parametrize("doi_list", TRIM_DEDUPE_LIST_DATA)
@pytest.mark.parametrize("doi_file", FILE_LIST_TEST_DATA)
def test_retrieve_doi_list_errors(
    doi_file, doi_list, source, save_dir, output_format_list, capsys
):
    error_list = []
    for parameter in [doi_list, doi_file, source, save_dir, output_format_list]:
        if "error" in parameter:
            error_list.append(parameter["error"])

    if not error_list:
        return

    # TODO: better error matching for tests
    error_match = "(Please check the above errors and try again|validation errors? for ValidateRetrieveDoiListInput)"
    with pytest.raises(ValueError, match=error_match):
        base.retrieve_doi_list(
            doi_list=doi_list["input"],
            doi_file=doi_file["input"],
            source=source["input"],
            output_format_list=output_format_list["input"],
            save_files=True,
            save_dir=save_dir["input"],
        )


@pytest.mark.parametrize("output_format_list", OUTPUT_FORMAT_LIST)
@pytest.mark.parametrize("save_to", SAVE_PARAMS)
@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
@pytest.mark.parametrize("doi_input_test_data", DOI_INPUT_TEST_DATA)
def test_retrieve_doi_list(
    doi_input_test_data,
    source,
    save_to,
    output_format_list,
    capsys,
    monkeypatch,
    _mock_response,
):
    """Test the retrieval of a list of DOIs from a source.

    :param doi_input: list of two test DOIs
    :type doi_input: list[str]
    :param source: data source
    :type source: str
    :param save_to: instructions on where to save downloaded data (if applicable)
    :type save_to: dict[str, str]
    :param output_format_set: formats to fetch the data in
    :type output_format_set: set[str]
    :param capsys: capture stdout/stderr
    :type capsys: pytest innards
    :param monkeypatch: monkeypatch functions
    :type monkeypatch: pytest monkeypatch
    """
    deduped_output_format_list = list(set(output_format_list))
    doi_input = copy.deepcopy(doi_input_test_data)

    is_crossref = source == CE.CROSSREF

    if "doi_file" in doi_input:
        prefix = "XR" if is_crossref else "DC"
        doi_input["doi_file"] = DOI_FILE[f"{prefix}_{doi_input['doi_file']}"]

    for list_name in ["doi_list", "all_dois"]:
        if list_name in doi_input:
            doi_input[list_name] = [
                TRANSLATED_DOI[is_crossref][li] for li in doi_input[list_name]
            ]

    doi_params = copy.deepcopy(doi_input)
    del doi_params["all_dois"]

    # expect an error if any of the output_format_list formats are wrong
    no_format = [fmt for fmt in output_format_list if fmt not in DATA_FORMAT[source]]
    if no_format:
        with pytest.raises(ValueError, match="Invalid output format"):
            base.retrieve_doi_list(
                **doi_params, source=source, output_format_list=output_format_list
            )
        return

    # pytest's tmp_path does not create a new dir for each run of the tests, hence the use of tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        default_dir = tmp_path / "default_dir"
        specified_dir = tmp_path / "specified_dir"
        for client in CLIENT.values():
            monkeypatch.setattr(client, "SAMPLE_DATA_DIR", default_dir)

        # set up the expected output
        output_data = {}
        errors = []
        param = {
            **doi_params,
            "source": source,
            "output_format_list": output_format_list,
        }

        for d in doi_input["all_dois"]:
            if d not in output_data:
                output_data[d] = {}
            for fmt in deduped_output_format_list:
                output_data[d][fmt] = generate_response_for_doi(source, d, fmt)
                if output_data[d][fmt] is None:
                    errors.append(f"Request for {d} {fmt} failed with status code 404")

        # calculate the expected results
        file_list = []
        if save_to["id"] in ["save_to_dir", "save_to_default_dir"]:
            file_list = [
                f"{FILE_NAME[d]}{CE.EXT[fmt]}"
                for d in doi_input["all_dois"]
                for fmt in deduped_output_format_list
                if d in output_data and fmt in output_data[d] and output_data[d][fmt]
            ]

        # copy over file save settings
        if "save_files" in save_to:
            param["save_files"] = save_to["save_files"]

        # set up the appropriate directories
        if "save_dir" in save_to:
            # convert "tmp_path" to the value of tmp_path
            if save_to["save_dir"] == "tmp_path":
                param["save_dir"] = specified_dir
                # ensure the save dir exists
                Path.mkdir(specified_dir, parents=True)
                assert param["save_dir"].exists()
            else:
                param["save_dir"] = save_to["save_dir"]
        else:
            Path.mkdir(default_dir, parents=True)
            assert default_dir.exists()

        expected = {"file_list": file_list, "output": {"data": output_data}}
        if errors:
            expected["errors"] = errors

        common.run_retrieve_doi_list(
            param=param,
            expected=expected,
            default_dir=default_dir,
            tmp_path=tmp_path,
            capsys=capsys,
        )


SEARCHING_XR = "Searching Crossref..."
SEARCHING_DC = "Searching Datacite..."
DOIS_NOT_FOUND = "The following DOIs could not be found:"

STDOUT_MESSAGES = {
    "none_found": [
        SEARCHING_XR,
        "Found 0 DOIs at Crossref",
        SEARCHING_DC,
        "Found 0 DOIs at Datacite",
        DOIS_NOT_FOUND,
        NOT_FOUND_DOI_A,
        NOT_FOUND_DOI_B,
    ],
    "all_crossref": [
        SEARCHING_XR,
        "Found 2 DOIs at Crossref",
    ],
    "one_xr_one_dc": [
        SEARCHING_XR,
        "Found 1 DOI at Crossref",
        SEARCHING_DC,
        "Found 1 DOI at Datacite",
        DOIS_NOT_FOUND,
        NOT_FOUND_DOI_A,
        NOT_FOUND_DOI_B,
    ],
    "all_datacite_and_none": [
        SEARCHING_XR,
        "Found 0 DOIs at Crossref",
        SEARCHING_DC,
        "Found 2 DOIs at Datacite",
        DOIS_NOT_FOUND,
        NOT_FOUND_DOI_A,
        NOT_FOUND_DOI_B,
    ],
}

EXPECTED = {
    "none_found": {doi: {CE.JSON: None} for doi in [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B]},
    "all_crossref": {
        doi: {CE.JSON: generate_response_for_doi(CE.CROSSREF, doi, CE.JSON)}
        for doi in [VALID_XR_DOI_A, VALID_XR_DOI_B]
    },
    "all_datacite_and_none": {
        **{
            doi: {CE.JSON: generate_response_for_doi(CE.DATACITE, doi, CE.JSON)}
            for doi in [VALID_DC_DOI_A, VALID_DC_DOI_B]
        },
        **{doi: {CE.JSON: None} for doi in [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B]},
    },
    "one_xr_one_dc": {
        VALID_XR_DOI_A: {
            CE.JSON: generate_response_for_doi(CE.CROSSREF, VALID_XR_DOI_A, CE.JSON)
        },
        VALID_DC_DOI_A: {
            CE.JSON: generate_response_for_doi(CE.DATACITE, VALID_DC_DOI_A, CE.JSON)
        },
        NOT_FOUND_DOI_A: {CE.JSON: None},
        NOT_FOUND_DOI_B: {CE.JSON: None},
    },
}

RETRIEVE_DOIS_FROM_UNKNOWN_DATA = [
    pytest.param(
        {
            "doi_list": [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
            "id": "none_found",
        },
        id="list_none_found",
    ),
    pytest.param(
        {
            "doi_file": DOI_FILE["INVALID"],
            "id": "none_found",
        },
        id="file_none_found",
    ),
    pytest.param(
        {"doi_list": [VALID_XR_DOI_A, VALID_XR_DOI_B], "id": "all_crossref"},
        id="list_all_crossref",
    ),
    pytest.param(
        {"doi_file": DOI_FILE["XR_VALID"], "id": "all_crossref"},
        id="file_all_crossref",
    ),
    pytest.param(
        {
            "doi_list": [VALID_XR_DOI_A],
            "doi_file": DOI_FILE["XR_VALID"],
            "id": "all_crossref",
        },
        id="both_all_crossref",
    ),
    pytest.param(
        {
            "doi_list": [VALID_DC_DOI_B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
            "doi_file": DOI_FILE["DC_VALID"],
            "id": "all_datacite_and_none",
        },
        id="both_all_datacite_and_none",
    ),
    pytest.param(
        {
            "doi_list": [
                VALID_XR_DOI_A,
                VALID_DC_DOI_A,
                NOT_FOUND_DOI_A,
                NOT_FOUND_DOI_B,
            ],
            "id": "one_xr_one_dc",
        },
        id="list_one_xr_one_dc",
    ),
    pytest.param(
        {
            "doi_file": DOI_FILE["XR_DC_VALID"],
            "doi_list": [
                NOT_FOUND_DOI_B,
                NOT_FOUND_DOI_B,
                NOT_FOUND_DOI_B,
                NOT_FOUND_DOI_A,
                NOT_FOUND_DOI_A,
            ],
            "id": "one_xr_one_dc",
        },
        id="both_file_one_xr_one_dc",
    ),
    pytest.param(
        {
            "doi_file": DOI_FILE["INVALID"],
            "doi_list": [VALID_XR_DOI_A, VALID_DC_DOI_A],
            "id": "one_xr_one_dc",
        },
        id="both_one_xr_one_dc",
    ),
]


@pytest.mark.parametrize(
    "output_format_list",
    [pytest.param([CE.JSON], id="json"), pytest.param([], id="default")],
)
@pytest.mark.parametrize("param", RETRIEVE_DOIS_FROM_UNKNOWN_DATA)
def test_retrieve_doi_list_from_unknown(
    param, output_format_list, capsys, _mock_response
):
    expected = EXPECTED[param["id"]]
    stdout = STDOUT_MESSAGES[param["id"]]
    doi_params = copy.deepcopy(param)
    del doi_params["id"]

    results = base.retrieve_doi_list_from_unknown(
        **doi_params,
        output_format_list=output_format_list,
        save_files=False,
    )
    for doi in expected:
        assert results[CE.DATA][doi] == expected[doi]

    assert results == {CE.DATA: expected}
    common.check_stdout_for_errs(capsys, stdout)


# this is unlikely to happen unless there is some trickery afoot
def test__check_for_missing_dois_unlikely_error(capsys):
    doi_list = [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B]
    results_dict = {
        VALID_DC_DOI_A: {CE.JSON: None},
        VALID_XR_DOI_B: {CE.JSON: None},
    }

    assert set(base._check_for_missing_dois(doi_list, results_dict)) == set(doi_list)
    common.check_stdout_for_errs(
        capsys, [f"{doi} is not in the results!" for doi in doi_list]
    )
