import tempfile
from pathlib import Path

import pytest

import credit_engine.constants as CE
import tests.common as common
from credit_engine.errors import make_error
from credit_engine.parsers import crossref, datacite, doi, osti
from tests.conftest import (
    A_VALID_DOI,
    ANOTHER_VALID_DOI,
    CLEAN_DOI_LIST_DATA,
    INVALID_DOI,
    NOT_FOUND,
    generate_response_for_doi,
)

PARSER = {
    CE.CROSSREF: crossref,
    CE.DATACITE: datacite,
    CE.OSTI: osti,
}

SOURCE_TEST_DATA = [pytest.param(src, id=src) for src in PARSER]

DATA_FORMAT = {
    CE.CROSSREF: {
        CE.JSON: CE.EXT[CE.JSON],
        CE.UNIXREF: CE.EXT[CE.UNIXREF],
        CE.UNIXSD: CE.EXT[CE.UNIXSD],
    },
    CE.DATACITE: {
        CE.JSON: CE.EXT[CE.JSON],
        CE.XML: CE.EXT[CE.XML],
    },
    CE.OSTI: {
        CE.JSON: CE.EXT[CE.JSON],
        CE.XML: CE.EXT[CE.XML],
    },
}


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
            "doi": NOT_FOUND,
            "expected": None,
        },
        id="not_found",
    ),
]


GET_EXTENSION_TEST_DATA = [
    pytest.param(
        {
            "parser": datacite,
            "output_format": "JSON",
            "expected": datacite.FILE_EXTENSIONS["json"],
        },
        id="datacite_json",
    ),
    pytest.param(
        {
            "parser": crossref,
            "output_format": "json",
            "expected": crossref.FILE_EXTENSIONS["json"],
        },
        id="crossref_json",
    ),
    pytest.param(
        {
            "parser": osti,
            "output_format": "Json",
            "expected": osti.FILE_EXTENSIONS["json"],
        },
        id="osti_json",
    ),
    pytest.param(
        {
            "parser": crossref,
            "output_format": "UNIXREF",
            "expected": crossref.FILE_EXTENSIONS["unixref"],
        },
        id="crossref_unixref",
    ),
    pytest.param(
        {
            "parser": crossref,
            "output_format": "xml",
            "error": True,
        },
        id="crossref_xml",
    ),
    pytest.param(
        {
            "parser": datacite,
            "output_format": "unixsd",
            "error": True,
        },
        id="datacite_unixsd",
    ),
    pytest.param(
        {
            "parser": osti,
            "output_format": "unixref",
            "error": True,
        },
        id="osti_unixref",
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
        id="invalid_source",
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
    pytest.param(["json"], id="json"),
    # valid for Datacite, OSTI
    pytest.param(["json", "xml"], id="json_xml"),
    # valid for Datacite, OSTI
    pytest.param(["xml"], id="xml"),
    # valid for Crossref
    pytest.param(["json", "unixref", "json", "json"], id="json_unixref"),
    # valid for Crossref
    pytest.param(["unixsd", "unixref"], id="unixref_unixsd"),
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
            "input": ["rdfxml", "xml", "json", "duck types"],
            "error": make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: ["rdfxml", "duck types"]},
            ),
        },
        id="invalid_fmt_values",
    ),
    pytest.param(
        {
            "input": ["json"],
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
        id="absolute_save_dir",
    ),
    pytest.param(
        {
            "input": "does/not/exist",
            "error": "invalid save_dir: 'does/not/exist' does not exist or is not a directory",
        },
        id="relative_save_dir",
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

DOI_LIST = [
    pytest.param([A_VALID_DOI, ANOTHER_VALID_DOI], id="all_valid"),
    pytest.param([A_VALID_DOI, INVALID_DOI], id="some_valid"),
    pytest.param([NOT_FOUND, INVALID_DOI], id="all_invalid"),
]


@pytest.mark.parametrize("param", CHECK_DOI_SOURCE_TEST_DATA)
def test_check_doi_source(param, _mock_response):
    """Test the DOI source function

    :param param: doi: the DOI to query; expected: expected result
    :type param: pytest.param
    :param _mock_response: mock requests.get function
    :type _mock_response: pytest mock
    """
    assert doi.check_doi_source(param["doi"]) == param["expected"]


def test_get_extension_fail_bad_source():
    SOURCE = "not a real source"
    error_text = f"No parser for source {SOURCE}"
    with pytest.raises(ValueError, match=error_text):
        doi.get_extension(SOURCE, CE.JSON)


@pytest.mark.parametrize("output_format", [CE.JSON, CE.XML, CE.UNIXREF, CE.UNIXSD])
@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
def test_get_extension(source, output_format):

    expected = DATA_FORMAT.get(source, {}).get(output_format, None)
    if expected is None:
        error_text = make_error(
            "invalid_param",
            {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
        )
        with pytest.raises(ValueError, match=error_text):
            doi.get_extension(source, output_format)

    else:
        assert doi.get_extension(source, output_format) == expected
        assert doi.get_extension(source, output_format.upper()) == expected
        assert doi.get_extension(source, output_format.title()) == expected
        assert doi.get_extension(source, output_format.title().swapcase()) == expected


@pytest.mark.parametrize("output_format_list", INVALID_OUTPUT_FORMAT_LIST_TEST_DATA)
@pytest.mark.parametrize("save_dir", INVALID_SAVE_DIR_TEST_DATA)
@pytest.mark.parametrize("source", INVALID_SOURCE_TEST_DATA)
@pytest.mark.parametrize("doi_list", CLEAN_DOI_LIST_DATA)
def test_retrieve_doi_list_errors(
    doi_list, source, save_dir, output_format_list, capsys
):
    error_list = []
    for parameter in [doi_list, source, save_dir, output_format_list]:
        if "error" in parameter:
            error_list.append(parameter["error"])

    if not error_list:
        return

    # TODO: better tests
    error_match = "(Please check the above errors and try again|validation errors? for (Validate)?RetrieveDoiList(Input)?)"
    with pytest.raises(ValueError, match=error_match):
        doi.retrieve_doi_list(
            doi_list=doi_list["input"],
            source=source["input"],
            output_format_list=output_format_list["input"],
            save_files=True,
            save_dir=save_dir["input"],
        )


@pytest.mark.parametrize("output_format_list", OUTPUT_FORMAT_LIST)
@pytest.mark.parametrize("save_to", SAVE_PARAMS)
@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
@pytest.mark.parametrize("doi_list", DOI_LIST)
def test_retrieve_doi_list(
    doi_list, source, save_to, output_format_list, capsys, monkeypatch, _mock_response
):

    deduped_output_format_list = list(set(output_format_list))
    # expect an error if any of the output_format_list formats are wrong
    no_format = [fmt for fmt in output_format_list if fmt not in DATA_FORMAT[source]]
    if no_format:
        with pytest.raises(ValueError, match="Invalid output format"):
            doi.retrieve_doi_list(doi_list, source, output_format_list)
        return

    # pytest's tmp_path does not create a new dir for each run of the tests, hence the use of tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        default_dir = tmp_path / "default_dir"
        specified_dir = tmp_path / "specified_dir"
        for parser in PARSER.values():
            monkeypatch.setattr(parser, "SAMPLE_DATA_DIR", default_dir)

        # set up the expected output
        output_data = {}
        errors = []
        param = {
            "doi_list": doi_list,
            "source": source,
            "output_format_list": output_format_list,
        }

        for d in doi_list:
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
                f"{d}{CE.EXT[fmt]}"
                for d in doi_list
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

DOI_SET = set([
    '10.25982/65526.69/1755438',
    '10.25982/1608940',
    '10.25982/1722943',
    '10.25982/86723.65/1778009',
    '10.25982/73218.75/1777998',
    '10.25982/73221.117/1777993',
])

FILE_LIST = [
    pytest.param({
        "input": Path('tests') / 'data' / 'empty.txt',
        "doi_list": set()
    }, id="empty_file"),
    pytest.param({
        "input": Path('tests') / 'data' / 'doi_list_with_dupes.txt',
        "doi_list": DOI_SET,
    }, id="dois_with_dupes"),
    pytest.param({
        "input": "/does/not/exist",
        "error_type": FileNotFoundError,
    }, id="file_does_not_exist"),
    pytest.param({
        "input": "sample_data/osti",
        "error_type": IsADirectoryError,
    }, id="directory")
]
@pytest.mark.parametrize("param", FILE_LIST)
def test_import_dois_from_file(param, monkeypatch):

    def return_input(*args):
        return args

    monkeypatch.setattr(doi, 'retrieve_doi_list', return_input)

    if "doi_list" in param:
        returned_input = doi.import_dois_from_file(param["input"], CE.CROSSREF, [CE.JSON])
        assert set(returned_input[0]) == param["doi_list"]

    else:
        with pytest.raises(param["error_type"]):
            doi.import_dois_from_file(param["input"], CE.CROSSREF, [CE.JSON])
