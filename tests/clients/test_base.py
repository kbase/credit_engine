import copy
import re
import tempfile
from pathlib import Path

import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients import base
from tests import common
from tests.conftest import (
    CLIENT,
    DOI_FILE,
    FILE_NAME,
    NOT_FOUND_DOI_A,
    NOT_FOUND_DOI_B,
    SOURCE_TEST_DATA,
    SOURCE_X_FORMAT_TEST_DATA,
    VALID_DC_DOI_A,
    VALID_DC_DOI_B,
    VALID_XR_DOI_A,
    VALID_XR_DOI_B,
    generate_response_for_doi,
)

VALID_SOURCE = "osti"
VALID_DOI_LIST = ["abcde"]

VALID_SOURCE_TEST_DATA = [pytest.param(src, id=src) for src in CLIENT]

DOT_JSON = ".json"
DOT_XML = ".xml"

OUTPUT_FORMATS = [
    # valid for Crossref, DataCite, OSTI
    pytest.param({CE.JSON}, id="json"),
    pytest.param({CE.XML}, id="xml"),
    pytest.param({CE.JSON, CE.XML}, id="json_xml"),
]


@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
def test__validate_retrieve_dois_invalid_source(source):
    """Ensure that invalid data sources return an error."""
    if "error" in source:
        with pytest.raises(ValueError, match=re.escape(source["error"])):
            base._validate_retrieve_dois(**source["args"])
        return

    (params, _) = base._validate_retrieve_dois(
        **source["args"], doi_list=["one", "two", "three"]
    )
    assert params.source.value == source["output"]
    assert params.dois == {"one", "two", "three"}
    assert params.output_formats == {CE.OutputFormat.JSON}


SAVE_PARAMS = [
    pytest.param({"id": "no_save_no_dir", "args": {}}, id="no_save_no_dir"),
    pytest.param(
        {
            "id": "no_save",
            "args": {
                "save_files": False,
                "save_dir": "tmp_path",
            },
        },
        id="no_save",
    ),
    # TODO @ialarmedalien: https://github.com/kbase/credit_engine/issues/158
    # pytest.param(
    #     {
    #         "id": "save_to_default_dir",
    #         "args": {
    #             "save_files": True,
    #         }
    #     },
    #     id="save_to_default_dir",
    # ),
    pytest.param(
        {
            "id": "save_to_dir",
            "args": {
                "save_files": True,
                "save_dir": "tmp_path",
            },
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
            "output": [A, B],
        },
        id="list_all_valid",
    ),
    pytest.param(
        {
            "doi_list": [A, NOT_FOUND_DOI_B],
            "output": [A, NOT_FOUND_DOI_B],
        },
        id="list_some_valid",
    ),
    pytest.param(
        {
            "doi_list": [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
            "output": [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
        },
        id="list_all_invalid",
    ),
    pytest.param(
        {
            "doi_file": "VALID_INVALID",
            "output": [A, B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
        },
        id="file_some_valid",
    ),
    pytest.param(
        {
            "doi_list": [A, B],
            "doi_file": "INVALID",
            "output": [A, B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
        },
        id="list_valid_file_invalid",
    ),
    pytest.param(
        {
            "doi_list": [A, NOT_FOUND_DOI_B],
            "doi_file": "VALID",
            "output": [A, B, NOT_FOUND_DOI_B],
        },
        id="mixed_sources",
    ),
]
# mappings of A and B to the appropriate Crossref or DataCite DOI
TR_NOT_FOUND_DOI = {
    NOT_FOUND_DOI_A: NOT_FOUND_DOI_A,
    NOT_FOUND_DOI_B: NOT_FOUND_DOI_B,
}
TRANSLATED_DOI = {
    # True = crossref DOI, False = datacite DOI
    True: {A: VALID_XR_DOI_A, B: VALID_XR_DOI_B, **TR_NOT_FOUND_DOI},
    False: {A: VALID_DC_DOI_A, B: VALID_DC_DOI_B, **TR_NOT_FOUND_DOI},
}


@pytest.mark.usefixtures("_mock_response")
@pytest.mark.parametrize("save_to", SAVE_PARAMS)
@pytest.mark.parametrize("source_format", SOURCE_X_FORMAT_TEST_DATA)
@pytest.mark.parametrize("doi_input_test_data", DOI_INPUT_TEST_DATA)
def test_retrieve_dois(
    doi_input_test_data,
    source_format,
    save_to,
    capsys,
    monkeypatch,
):
    """Test the retrieval of a list of DOIs from a source.

    :param doi_input: list of two test DOIs
    :type doi_input: list[str]
    :param source: data source
    :type source: str
    :param save_to: instructions on where to save downloaded data (if applicable)
    :type save_to: dict[str, str]
    :param output_formats: formats to fetch the data in
    :type output_formats: set[str]
    :param capsys: capture stdout/stderr
    :type capsys: pytest innards
    :param monkeypatch: monkeypatch functions
    :type monkeypatch: pytest monkeypatch
    """
    source = source_format["args"]["source"]
    is_crossref = source == CE.CROSSREF

    doi_input = {}

    # use the appropriate DOI file for the source
    if "doi_file" in doi_input_test_data:
        prefix = "XR" if is_crossref else "DC"
        doi_input["doi_file"] = DOI_FILE[f"{prefix}_{doi_input_test_data['doi_file']}"]

    # swap out 'A' and 'B' for valid IDs
    for list_name in ["doi_list", "output"]:
        if list_name in doi_input_test_data:
            doi_input[list_name] = [
                TRANSLATED_DOI[is_crossref][li] for li in doi_input_test_data[list_name]
            ]

    param = copy.deepcopy(doi_input)
    del param["output"]
    param = {**param, **source_format["args"], **save_to["args"]}

    # expect an error if any of the output_formats are not in the
    # client's valid format list
    if "error" in source_format:
        with pytest.raises(ValueError, match=re.escape(source_format["error"][0])):
            base.retrieve_dois(**param)
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

        for d in doi_input["output"]:
            if d not in output_data:
                output_data[d] = {}
            for output_format in source_format["output"]:
                fmt = output_format.value
                output_data[d][fmt] = generate_response_for_doi(source, d, fmt)
                if output_data[d][fmt] is None:
                    errors.append(f"Request for {d} {fmt} failed with status code 404")

        # calculate the expected results
        file_list = []
        if save_to["id"] in ["save_to_dir", "save_to_default_dir"]:
            file_list = [
                f"{FILE_NAME[d]}{CE.EXT[fmt.value]}"
                for d in doi_input["output"]
                for fmt in source_format["output"]
                if d in output_data
                and fmt.value in output_data[d]
                and output_data[d][fmt.value]
            ]

        # set up the appropriate directories
        if "save_dir" in save_to["args"]:
            # convert "tmp_path" to the value of tmp_path
            if save_to["args"]["save_dir"] == "tmp_path":
                param["save_dir"] = specified_dir
                # ensure the save dir exists
                Path.mkdir(specified_dir, parents=True)
                assert param["save_dir"].exists()
        else:
            Path.mkdir(default_dir, parents=True)
            assert default_dir.exists()

        expected = {"file_list": file_list, "output": {"data": output_data}}
        if errors:
            expected["errors"] = errors

        common.run_retrieve_dois(
            param=param,
            output_formats=source_format["output"],
            expected=expected,
            default_dir=default_dir,
            tmp_path=tmp_path,
            capsys=capsys,
        )


SEARCHING_XR = "Searching Crossref..."
SEARCHING_DC = "Searching DataCite..."
DOIS_NOT_FOUND = "The following DOIs could not be found:"

STDOUT_MESSAGES = {
    "none_found": [
        SEARCHING_XR,
        "Found 0 DOIs at Crossref",
        SEARCHING_DC,
        "Found 0 DOIs at DataCite",
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
        "Found 1 DOI at DataCite",
        DOIS_NOT_FOUND,
        NOT_FOUND_DOI_A,
        NOT_FOUND_DOI_B,
    ],
    "all_datacite_and_none": [
        SEARCHING_XR,
        "Found 0 DOIs at Crossref",
        SEARCHING_DC,
        "Found 2 DOIs at DataCite",
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
            "args": {
                "doi_list": [NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
            },
            "id": "none_found",
        },
        id="list_none_found",
    ),
    pytest.param(
        {
            "args": {
                "doi_file": DOI_FILE["INVALID"],
            },
            "id": "none_found",
        },
        id="file_none_found",
    ),
    pytest.param(
        {
            "args": {
                "doi_list": [VALID_XR_DOI_A, VALID_XR_DOI_B],
            },
            "id": "all_crossref",
        },
        id="list_all_crossref",
    ),
    pytest.param(
        {
            "args": {
                "doi_file": DOI_FILE["XR_VALID"],
            },
            "id": "all_crossref",
        },
        id="file_all_crossref",
    ),
    pytest.param(
        {
            "args": {
                "doi_list": [VALID_XR_DOI_A],
                "doi_file": DOI_FILE["XR_VALID"],
            },
            "id": "all_crossref",
        },
        id="both_all_crossref",
    ),
    pytest.param(
        {
            "args": {
                "doi_list": [VALID_DC_DOI_B, NOT_FOUND_DOI_A, NOT_FOUND_DOI_B],
                "doi_file": DOI_FILE["DC_VALID"],
            },
            "id": "all_datacite_and_none",
        },
        id="both_all_datacite_and_none",
    ),
    pytest.param(
        {
            "args": {
                "doi_list": [
                    VALID_XR_DOI_A,
                    VALID_DC_DOI_A,
                    NOT_FOUND_DOI_A,
                    NOT_FOUND_DOI_B,
                ],
            },
            "id": "one_xr_one_dc",
        },
        id="list_one_xr_one_dc",
    ),
    pytest.param(
        {
            "args": {
                "doi_file": DOI_FILE["XR_DC_VALID"],
                "doi_list": [
                    NOT_FOUND_DOI_B,
                    NOT_FOUND_DOI_B,
                    NOT_FOUND_DOI_B,
                    NOT_FOUND_DOI_A,
                    NOT_FOUND_DOI_A,
                ],
            },
            "id": "one_xr_one_dc",
        },
        id="both_file_one_xr_one_dc",
    ),
    pytest.param(
        {
            "args": {
                "doi_file": DOI_FILE["INVALID"],
                "doi_list": [VALID_XR_DOI_A, VALID_DC_DOI_A],
            },
            "id": "one_xr_one_dc",
        },
        id="both_one_xr_one_dc",
    ),
]


@pytest.mark.parametrize(
    "output_formats",
    [
        pytest.param({"output_formats": {CE.JSON}}, id="json"),
        pytest.param({}, id="default"),
    ],
)
@pytest.mark.parametrize("param", RETRIEVE_DOIS_FROM_UNKNOWN_DATA)
def test_retrieve_dois_from_unknown(param, output_formats, capsys):
    expected = EXPECTED[param["id"]]
    stdout = STDOUT_MESSAGES[param["id"]]

    results = base.retrieve_dois_from_unknown(
        **param["args"],
        **output_formats,
        save_files=False,
    )
    for doi in expected:
        assert results[CE.DATA][doi] == expected[doi]

    assert results == {CE.DATA: expected}
    common.check_stdout_for_errs(capsys, stdout)


# this is unlikely to happen unless there is some trickery afoot
def test__check_for_missing_dois_unlikely_error(capsys):
    doi_list = {NOT_FOUND_DOI_A, NOT_FOUND_DOI_B}
    results_dict = {
        VALID_DC_DOI_A: {CE.JSON: None},
        VALID_XR_DOI_B: {CE.JSON: None},
    }

    assert base._check_for_missing_dois(doi_list, results_dict) == doi_list
    common.check_stdout_for_errs(
        capsys, [f"{doi} is not in the results!" for doi in doi_list]
    )
